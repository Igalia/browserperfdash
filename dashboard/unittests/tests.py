from django.test import TransactionTestCase
from dashboard.models import Bot, BotReportData, CPUArchitecture, GPUType, Platform, Browser, Test, \
    MetricUnit
from rest_framework.test import APIClient
from collections import OrderedDict

client = APIClient()


class BotReportDataTestCase(TransactionTestCase):
    bot_id = "test_bot"
    bot_password = "test_pwd"
    test_version = "https://test.dummy.org/test_root_test/@r182170"
    browser_version = 'test_browser_version'
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
        # Try POSTing to the path, and cehck if the data went well
        upload_data = OrderedDict([
            ('bot_id', self.bot_id),('bot_password', self.bot_password), ('browser_id', 'test_browser'),
            ('browser_version', self.browser_version), ('test_id', self.root_test),
            ('test_version', self.test_version),
            ('test_data', '{"RootTest": {"metrics": {"Time": ["Total", "Arithmetic"]},'
                          '"tests": {"SubTest1": {"metrics": {"Time": {"current": [1, 2, 3]}}},'
                          '"SubTest2": {"metrics": {"Time": {"current": [4, 5, 6]}}}}}}'
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

        # RootTest:Time:Arithmetic: 3.0ms stdev=33.3%
        root_test1 = bot_report_obj.get(test_path='RootTest', metric_unit='Time', aggregation='Arithmetic')
        self.assertEqual(root_test1.mean_value, 3.0)
        self.assertEqual(round(root_test1.stddev*100, 1), 33.3)

        # RootTest:Time:Total: 7.0ms stdev=28.6%
        root_test2 = bot_report_obj.get(test_path='RootTest', metric_unit='Time', aggregation='Total')
        self.assertEqual(root_test2.mean_value, 7.0)
        self.assertEqual(round(root_test2.stddev * 100, 1), 28.6)
