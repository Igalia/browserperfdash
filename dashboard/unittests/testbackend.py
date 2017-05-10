from django.test import TransactionTestCase
from dashboard.models import Bot, BotReportData, CPUArchitecture, GPUType, Platform, Browser, Test, \
    MetricUnit
from rest_framework.test import APIClient
from collections import OrderedDict
from datetime import datetime

client = APIClient()


class BotReportDataTestCase(TransactionTestCase):
    bot_id = "test_bot"
    bot_password = "test_pwd"
    test_version = "https://test.dummy.org/test_root_test/@r182170"
    test_version_next_ver = "https://test.dummy.org/test_root_test/@r182500"
    browser_version = 'test_browser_version'
    browser_version_next_ver = 'test_browser_version_next_ver'
    root_test = "RootTest"

    def setUp(self):
        test_cpu_arch = CPUArchitecture.objects.create(name='test_cpu', enabled=True)
        test_gpu_type = GPUType.objects.create(name='test_gpu', enabled=True)
        test_platform = Platform.objects.create(name='test_platform', enabled=True)
        Bot.objects.create(
            password=self.bot_password, name=self.bot_id, cpuArchitecture=test_cpu_arch,
            cpuDetail='test_cpu_detail', gpuType=test_gpu_type, gpuDetail='test_gpu_detail',
            platform=test_platform, platformDetail='test_platform_detail', enabled=True
        )
        Browser.objects.create(id='test_browser', name='Test_Browser', enabled=True)
        Test.objects.create(
            id=self.root_test, description='test_root_test_desc', url='http://something_here.com',
            enabled=True
        )
        MetricUnit.objects.bulk_create([
            MetricUnit(
                name='Score', unit='pt', description='test_description_score', prefix=[{"unit": 1.0, "symbol": 'pt'}]
            ),
            MetricUnit(
                name='Time', unit='ms', description='test_description_time', prefix=[{"unit": 1.0, "symbol": 'ms'}]
            )
        ])

    def test_bot_authentications(self):
        """Test all possible authentication cases"""
        upload_data = OrderedDict([
            ('bot_id', self.bot_id+self.bot_id),('bot_password', self.bot_password), ('browser_id', 'test_browser'),
            ('browser_version', self.browser_version), ('test_id', self.root_test),
            ('test_version', self.test_version),
            ('test_data', '{"RootTest": {"metrics": {"Time": {"current": [1, 2, 3]},"Score": {"current": [2, 3, 4]}}}}')
        ])
        response = client.post('/dash/bot-report/', dict(upload_data))
        self.assertEqual(response.data['detail'], "This bot cannot be authenticated")

        # Try POSTing with wrong password, and cehck if the data went well
        upload_data = OrderedDict([
            ('bot_id', self.bot_id),('bot_password', self.bot_password+self.bot_password ), ('browser_id', 'test_browser'),
            ('browser_version', self.browser_version), ('test_id', self.root_test),
            ('test_version', self.test_version),
            ('test_data', '{"RootTest": {"metrics": {"Time": {"current": [1, 2, 3]},"Score": {"current": [2, 3, 4]}}}}')
        ])
        response = client.post('/dash/bot-report/', dict(upload_data))
        self.assertEqual(response.data['detail'],"Bad authentication details")
        self.assertEqual(BotReportData.objects.all().count(), 0)

    def test_data_no_aggregation_uploaded_correctly(self):
        # Try POSTing to the path, and cehck if the data went well
        upload_data = OrderedDict([
            ('bot_id', self.bot_id),('bot_password', self.bot_password), ('browser_id', 'test_browser'),
            ('browser_version', self.browser_version), ('test_id', self.root_test),
            ('test_version', self.test_version),
            ('test_data', '{"RootTest": {"metrics": {"Time": {"current": [1, 2, 3]},"Score": {"current": [2, 3, 4]}}}}')
        ])
        response = client.post('/dash/bot-report/', dict(upload_data))
        self.assertEqual(response.status_code, 200)

        # There should be two objects created
        self.assertEqual(BotReportData.objects.all().count(), 2)

        # Check for individual items
        score_object = BotReportData.objects.get(metric_unit='Score')
        time_object = BotReportData.objects.get(metric_unit='Time')

        self.assertEqual(score_object.mean_value, 3.0)
        self.assertEqual(round(score_object.stddev*100, 1), 33.3)
        self.assertEqual(time_object.mean_value, 2.0)
        self.assertEqual(round(time_object.stddev*100, 1), 50.0)

        self.assertEqual(score_object.prev_result, None)
        self.assertEqual(time_object.prev_result, None)

    def test_with_more_complicated_data(self):
        """
        [{'value': 7.0, 'name': 'RootTest', 'unit': 'ms', 'metric': 'Time\\Total', 'stdev': 0.2857142857142857},
        {'value': 3.5, 'name': 'RootTest', 'unit': 'ms', 'metric': 'Time\\Arithmetic', 'stdev': 0.2857142857142857},
        {'value': 2.0, 'name': 'RootTest\\SubTest1', 'unit': 'ms', 'metric': 'Time\\None', 'stdev': 0.5},
        {'value': 5.0, 'name': 'RootTest\\SubTest2', 'unit': 'ms', 'metric': 'Time\\None', 'stdev': 0.2}]
        """
        # Try POSTing to the path, and cehck if the data went well
        upload_data = OrderedDict([
            ('bot_id', self.bot_id),('bot_password', self.bot_password), ('browser_id', 'test_browser'),
            ('browser_version', self.browser_version), ('test_id', self.root_test),
            ('test_version', self.test_version),
            ('test_data', '{"RootTest": {"metrics": {"Time": ["Total", "Arithmetic"]},"tests": {"SubTest1": {"metrics": {"Time": {"current": [1, 2, 3]}}},"SubTest2": {"metrics": {"Time": {"current": [4, 5, 6]}}}}}}'
             )
        ])
        response = client.post('/dash/bot-report/', dict(upload_data))
        self.assertEqual(response.status_code, 200)
        bot_report_obj = BotReportData.objects.all()

        # There should be 4 report rows from the above processed data
        self.assertEqual(bot_report_obj.count(), 4)
        for report in bot_report_obj:
            # There should be no previous result at this point as aggregations are different for each results
            self.assertEqual(report.prev_result, None)
            self.assertEqual(report.delta, 0)

        # RootTest\SubTest1:Time: 2.0ms stdev=50.0%
        subtest1 = bot_report_obj.get(test_path='RootTest\SubTest1', metric_unit='Time', aggregation='None')
        self.assertEqual(subtest1.mean_value, 2.0)
        self.assertEqual(round(subtest1.stddev*100, 1), 50.0)

        # RootTest\SubTest2:Time: 5.0ms stdev=20.0%
        subtest2 = bot_report_obj.get(test_path='RootTest\SubTest2', metric_unit='Time', aggregation='None')
        self.assertEqual(subtest2.mean_value, 5.0)
        self.assertEqual(round(subtest2.stddev * 100, 1), 20.0)

        # RootTest:Time:Arithmetic: 3.5ms stdev=33.3%
        root_test1 = bot_report_obj.get(test_path='RootTest', metric_unit='Time', aggregation='Arithmetic')
        self.assertEqual(root_test1.mean_value, 3.5)
        self.assertEqual(round(root_test1.stddev*100, 1), 28.6)

        # RootTest:Time:Total: 7.0ms stdev=28.6%
        root_test2 = bot_report_obj.get(test_path='RootTest', metric_unit='Time', aggregation='Total')
        self.assertEqual(root_test2.mean_value, 7.0)
        self.assertEqual(round(root_test2.stddev * 100, 1), 28.6)

    def test_previous_result_with_some_real_data(self):
        """
        timestamp = 1493981500;
        Should end up creating report data for a data with the below one.
        {'metric': u'Score\\None', 'unit': 'pt', 'name': u'SpeedometerExample', 'value': 142.0, 'stdev': 0.007042253521126761}
        {'metric': u'Time\\Total', 'unit': 'ms', 'name': u'SpeedometerExample', 'value': 41405200016.409996, 'stdev': 2.2357169550550746}
        {'metric': u'Time\\Total', 'unit': 'ms', 'name': u'SpeedometerExample\\AngularJS-TodoMVC', 'value': 41405200016.409996, 'stdev': 2.2357169550550746}
        {'metric': u'Time\\Total', 'unit': 'ms', 'name': u'SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items', 'value': 41405200016.409996, 'stdev': 2.2357169550550746}
        {'metric': u'Time\\None', 'unit': 'ms', 'name': u'SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items\\Async', 'value': 11.25, 'stdev': 0.17356110390903676}
        {'metric': u'Time\\None', 'unit': 'ms', 'name': u'SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items\\Sync', 'value': 41405200005.159996, 'stdev': 2.2357169556929097}

        and then later at timestamp = 1493981600;
        {'metric': u'Score\\None', 'unit': 'pt', 'name': u'SpeedometerExample', 'value': 146.0, 'stdev': 0.010829718014275272}
        {'metric': u'Time\\Total', 'unit': 'ms', 'name': u'SpeedometerExample', 'value': 61407800017.409996, 'stdev': 2.235712954065906}
        {'metric': u'Time\\Total', 'unit': 'ms', 'name': u'SpeedometerExample\\AngularJS-TodoMVC', 'value': 61407800017.409996, 'stdev': 2.235712954065906}
        {'metric': u'Time\\Total', 'unit': 'ms', 'name': u'SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items', 'value': 61407800017.409996, 'stdev': 2.235712954065906}
        {'metric': u'Time\\None', 'unit': 'ms', 'name': u'SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items\\Async', 'value': 12.25, 'stdev': 0.15939285052870722}
        {'metric': u'Time\\None', 'unit': 'ms', 'name': u'SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items\\Sync', 'value': 61407800005.159996, 'stdev': 2.2357129545323837}
        """
        Test.objects.create(
            id="SpeedometerExample", description='SpeedometerExample test', url='http://something_here.com',
            enabled=True
        )
        # Try POSTing to the path, and check if the data went well
        upload_data = OrderedDict([
            ('bot_id', self.bot_id),('bot_password', self.bot_password), ('browser_id', 'test_browser'),
            ('browser_version', self.browser_version), ('test_id', "SpeedometerExample"),
            ('test_version', self.test_version), ('timestamp', 1493981500),
            ('test_data', '{"SpeedometerExample":{"metrics":{"Score":{"current":[142,141,143,141,143]},'
                          '"Time":["Total"]},"tests":{"AngularJS-TodoMVC":{"metrics":{"Time":["Total"]},'
                          '"tests":{"Adding100Items":{"metrics":{"Time":["Total"]},'
                          '"tests":{"Async":{"metrics":{"Time":{"current":[9,11,10,12.25,14]}}},'
                          '"Sync":{"metrics":{"Time":{"current":[207000000000,1900008,20000014,2000003.8,2100000]'
                          '}}}}}}}}}}'
             )
        ])
        response = client.post('/dash/bot-report/', dict(upload_data))
        self.assertEqual(response.status_code, 200)

        initial_ver_timestamp_datetime = datetime.fromtimestamp(float(1493981500))
        self.assertEqual(BotReportData.objects.all().filter(timestamp=initial_ver_timestamp_datetime).count(), 6)

        # Try POSTing to the path, and check if the data went well
        upload_data_next_ver = OrderedDict([
            ('bot_id', self.bot_id),('bot_password', self.bot_password), ('browser_id', 'test_browser'),
            ('browser_version', self.browser_version_next_ver), ('test_id', "SpeedometerExample"),
            ('test_version', self.test_version_next_ver), ('timestamp', 1493981600),
            ('test_data', '{"SpeedometerExample":{"metrics":{"Score":{"current":[144,145,146,147,148]},'
                          '"Time":["Total"]},"tests":{"AngularJS-TodoMVC":{"metrics":{"Time":["Total"]},'
                          '"tests":{"Adding100Items":{"metrics":{"Time":["Total"]},'
                          '"tests":{"Async":{"metrics":{"Time":{"current":[10,12,11,13.25,15]}}},'
                          '"Sync":{"metrics":{"Time":{"current":[307000000000,2900008,30000014,3000003.8,3100000]'
                          '}}}}}}}}}}'
             )
        ])
        response = client.post('/dash/bot-report/', dict(upload_data_next_ver))
        self.assertEqual(response.status_code, 200)

        next_ver_timestamp_datetime = datetime.fromtimestamp(float(1493981600))
        self.assertEqual(BotReportData.objects.all().filter(timestamp=next_ver_timestamp_datetime).count(), 6)

        bot_reports_full = BotReportData.objects.all()
        # verify previous_results were populated correctly
        for report in bot_reports_full.filter(timestamp=initial_ver_timestamp_datetime):
            self.assertEqual(report.prev_result, None)

        # verify if delta was correctly processed and added to
        for report in bot_reports_full.filter(timestamp=next_ver_timestamp_datetime):
            # a precision upto 5 is good enough ?
            self.assertEqual(
                round(report.delta, 5),
                round(abs(1 - float(report.prev_result.mean_value) / float(report.mean_value))* 100.00, 5)
            )

            # Verify if the previous result is set correctly
            self.assertEqual(
                report.prev_result,
                BotReportData.objects.get(
                    browser=report.browser, root_test=report.root_test, test_path=report.test_path,
                    metric_unit=report.metric_unit, aggregation=report.aggregation, timestamp=initial_ver_timestamp_datetime
                )
            )