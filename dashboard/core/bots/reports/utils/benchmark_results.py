# Copyright (C) 2015 Apple Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1.  Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY APPLE INC. AND ITS CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL APPLE INC. OR ITS CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import math
import re


class BenchmarkResults(object):

    aggregators = {
        'Total': (lambda values: sum(values)),
        'Arithmetic': (lambda values: float(sum(values)) / len(values)),
        'Geometric': (lambda values: math.exp(sum(map(math.log, values)) / len(values))),
    }
    metric_to_unit = {
        'FrameRate': 'fps',
        'Runs': '/s',
        'Time': 'ms',
        'Duration': 'ms',
        'Malloc': 'B',
        'Heap': 'B',
        'Allocations': 'B',
        'Score': 'pt',
        'BrowserMemoryUsage': 'B',
        'BrowserMemoryPeak': 'B',
    }
    SI_prefixes = ['n', 'u', 'm', '', 'K', 'M', 'G', 'T', 'P', 'E']
    db_character_separator = '\\' # This is '\' but escaped

    _results = None

    def __init__(self, results):
        self._lint_results(results)
        self._results = self._aggregate_results(results)

    def format(self, scale_unit=True):
        return self._format_tests(self._results, scale_unit)

    def format_dict(self):
        return self._format_dict_results(self._results)

    def format_json(self):
        return json.dumps(self.format_dict(), indent=True)

    def set_values(self, result):
        self._results = None
        self._lint_results(result)
        self._results = self._aggregate_results(result)

    def fetch_db_entries(self, skip_aggregated=False):
        test_table = []
        return self._generate_db_entries(self._results,test_table, skip_aggregated)

    def print_db_entries(self, skip_aggregated=False):
        test_table = []
        db_entries = self._generate_db_entries(self._results, test_table, skip_aggregated)
        for db_entry in db_entries:
            print(('Name=%s \t Metric=%s \t Unit=%s \t Value=%s \t Stdev=%s' %(db_entry['name'], db_entry['metric'],
                                                                              db_entry['unit'], db_entry['value'], db_entry['stdev'])))

    def __del__(self):
        self._results = None

    """
    The method below returns a list of dictionaries, with the following format (backward-slashes are escaped):

    [{'name': SpeedometerExample, 'metric': Score\\None, 'value': 142.0, 'stdev': 0.00704225352113}
    {'name': SpeedometerExample, 'metric': Time\\Total, 'value': 674.22, 'stdev': 0.098284410446}
    {'name': SpeedometerExample\\AngularJS-TodoMVC, 'metric': Time:Total, 'value': 674.22, 'stdev': 0.098284410446}
    {'name': SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items, 'metric': Time\\Total, 'value': 217.81, 'stdev': 0.0290934151339}
    {'name': SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items, 'metric': Time\\Total, 'value': 217.81, 'stdev': 0.0290934151339}
    {'name': SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items\\Async, 'metric': Time\\None, 'value': 11.25, 'stdev': 0.173561103909}
    {'name': SpeedometerExample\\AngularJS-TodoMVC\\Adding100Items\\Sync, 'metric': Time\\None, 'value': 206.56, 'stdev': 0.0294749686776}
    {'name': SpeedometerExample\\AngularJS-TodoMVC\\Adding200Items, 'metric': Time\\Total, 'value': 456.41, 'stdev': 0.136262489719}
    {'name': SpeedometerExample\\AngularJS-TodoMVC\\Adding200Items\\Async, 'metric': Time\\None, 'value': 27.25, 'stdev': 0.395773479085}
    {'name': SpeedometerExample\\AngularJS-TodoMVC\\Adding200Items\\Sync, 'metric': Time\\None, 'value': 429.16, 'stdev': 0.122973388375}]

    The Value of the metric field indicates the metric and the aggregator.
    It uses the character \\ as separator, so it contains metric:aggregator
    If aggregator is "None" then it means its a real value (not aggregated)
    """
    @classmethod
    def _generate_db_entries(cls, tests, test_table, skip_aggregated=False, parent=None):
        for test_name in sorted(tests.keys()):
            if cls.db_character_separator in test_name:
                raise ValueError('Test %s contains a "%s" in the name. This is Forbidden' %(test_name, cls.db_character_separator))
            if parent is None:
                test_path = test_name
            else:
                test_path = '%s%s%s' %(parent, cls.db_character_separator, test_name)

            for unit in sorted(tests[test_name]['metrics'].keys()):
                for aggregator in list(tests[test_name]['metrics'][unit].keys()):
                    if skip_aggregated:
                        if aggregator is not None:
                            continue
                    values = cls._format_values(unit, tests[test_name]['metrics'][unit][aggregator]['current'], db_format=True)
                    test_table.append({'name': test_path,
                                       'metric': '%s%s%s' %(unit, cls.db_character_separator, aggregator),
                                       'value': values['value'],
                                       'stdev': values['stdev'],
                                       'unit': values['unit'],
                                       })

            if 'tests' in tests[test_name]:
                BenchmarkResults._generate_db_entries(tests[test_name]['tests'], test_table, skip_aggregated, test_path)

        return test_table



    @classmethod
    def _format_dict_results(cls, tests):
        format_dict = {}
        for test_name in sorted(tests.keys()):
            if test_name in format_dict:
                raise NotImplementedError
            format_dict[test_name] = {}
            format_dict[test_name]['metrics'] = {}

            # Fill metric_to_unit and aggregator/None
            for unit in sorted(tests[test_name]['metrics'].keys()):
                format_dict[test_name]['metrics'][unit] = {}
                for aggregator in list(tests[test_name]['metrics'][unit].keys()):
                    format_dict[test_name]['metrics'][unit][aggregator] = cls._format_values(unit, tests[test_name]['metrics'][unit][aggregator]['current'], json_format=True)

            if 'tests' in tests[test_name]:
                format_dict[test_name]['tests'] = BenchmarkResults._format_dict_results(tests[test_name]['tests'])

        return format_dict

    @classmethod
    def _format_tests(cls, tests, scale_unit, indent=''):
        output = ''
        config_name = 'current'
        for test_name in sorted(tests.keys()):
            is_first = True
            test = tests[test_name]
            metrics = test.get('metrics', {})
            for metric_name in sorted(metrics.keys()):
                metric = metrics[metric_name]
                for aggregator_name in sorted(metric.keys()):
                    output += indent
                    if is_first:
                        output += test_name
                        is_first = False
                    else:
                        output += ' ' * len(test_name)
                    output += ':' + metric_name + ':'
                    if aggregator_name:
                        output += aggregator_name + ':'
                    output += ' ' + cls._format_values(metric_name, metric[aggregator_name][config_name], scale_unit) + '\n'
            if 'tests' in test:
                output += cls._format_tests(test['tests'], scale_unit, indent=(indent + ' ' * len(test_name)))
        return output

    @classmethod
    def _format_values(cls, metric_name, values, scale_unit=True, json_format=False, db_format=False):
        values = list(map(float, values))
        total = sum(values)
        mean = total / len(values)
        square_sum = sum([x * x for x in values])
        sample_count = len(values)

        # With sum and sum of squares, we can compute the sample standard deviation in O(1).
        # See https://rniwa.com/2012-11-10/sample-standard-deviation-in-terms-of-sum-and-square-sum-of-samples/
        if sample_count <= 1:
            sample_stdev = 0
        else:
            # Be careful about round-off error when sample_stdev is 0.
            sample_stdev = math.sqrt(max(0, square_sum / (sample_count - 1) - total * total / (sample_count - 1) / sample_count))

        unit = cls._unit_from_metric(metric_name)

        # scale unit is ignored for db_format, we get the raw values always
        if db_format:
            return {'value': mean, 'stdev':  sample_stdev / mean, 'unit': unit}

        if json_format:
            return {'mean_value': mean, 'stdev':  sample_stdev / mean, 'unit': unit, 'raw_values': values}

        if not scale_unit:
            return ('{mean:.3f}{unit} stdev={delta:.1%}').format(mean=mean, delta=sample_stdev / mean, unit=unit)

        if unit == 'ms':
            unit = 's'
            mean = float(mean) / 1000
            sample_stdev /= 1000

        base = 1024 if unit == 'B' else 1000
        value_sig_fig = 1 - math.floor(math.log10(sample_stdev / mean)) if sample_stdev else 3
        SI_magnitude = math.floor(math.log(mean, base))

        scaled_mean = mean * math.pow(base, -SI_magnitude)
        SI_prefix = cls.SI_prefixes[int(SI_magnitude) + 3]

        non_floating_digits = 1 + math.floor(math.log10(scaled_mean))
        floating_points_count = max(0, value_sig_fig - non_floating_digits)
        return ('{mean:.' + str(int(floating_points_count)) + 'f}{prefix}{unit} stdev={delta:.1%}').format(
            mean=scaled_mean, delta=sample_stdev / mean, prefix=SI_prefix, unit=unit)

    @classmethod
    def _unit_from_metric(cls, metric_name):
        # FIXME: Detect unknown mettric names
        suffix = re.match(r'.*?([A-z][a-z]+|FrameRate)$', metric_name)
        return cls.metric_to_unit[suffix.group(1)]

    @classmethod
    def _aggregate_results(cls, tests):
        results = {}
        for test_name, test in tests.items():
            results[test_name] = cls._aggregate_results_for_test(test)
        return results

    @classmethod
    def _aggregate_results_for_test(cls, test):
        subtest_results = cls._aggregate_results(test['tests']) if 'tests' in test else {}
        results = {}
        for metric_name, metric in test.get('metrics', {}).items():
            if not isinstance(metric, list):
                results[metric_name] = {None: {}}
                for config_name, values in metric.items():
                    results[metric_name][None][config_name] = cls._flatten_list(values)
                continue

            aggregator_list = metric
            results[metric_name] = {}
            for aggregator in aggregator_list:
                values_by_config_iteration = cls._subtest_values_by_config_iteration(subtest_results, metric_name, aggregator)
                for config_name, values_by_iteration in values_by_config_iteration.items():
                    results[metric_name].setdefault(aggregator, {})
                    results[metric_name][aggregator][config_name] = [cls._aggregate_values(aggregator, values) for values in values_by_iteration]

        return {'metrics': results, 'tests': subtest_results}

    @classmethod
    def _flatten_list(cls, nested_list):
        flattened_list = []
        for item in nested_list:
            if isinstance(item, list):
                flattened_list += cls._flatten_list(item)
            else:
                flattened_list.append(item)
        return flattened_list

    @classmethod
    def _subtest_values_by_config_iteration(cls, subtest_results, metric_name, aggregator):
        values_by_config_iteration = {}
        for subtest_name, subtest in subtest_results.items():
            results_for_metric = subtest['metrics'].get(metric_name, {})
            results_for_aggregator = results_for_metric.get(aggregator, results_for_metric.get(None, {}))
            for config_name, values in results_for_aggregator.items():
                values_by_config_iteration.setdefault(config_name, [[] for _ in values])
                for iteration, value in enumerate(values):
                    values_by_config_iteration[config_name][iteration].append(value)
        return values_by_config_iteration

    @classmethod
    def _aggregate_values(cls, aggregator, values):
        return cls.aggregators[aggregator](values)

    @classmethod
    def _lint_results(cls, tests):
        cls._lint_subtest_results(tests, None)
        return True

    @classmethod
    def _lint_subtest_results(cls, subtests, parent_needing_aggregation):
        iteration_groups_by_config = {}
        for test_name, test in list(subtests.items()):
            needs_aggregation = False

            if 'metrics' not in test and 'tests' not in test:
                raise TypeError('"%s" does not contain metrics or tests' % test_name)

            if 'metrics' in test:
                metrics = test['metrics']
                if not isinstance(metrics, dict):
                    raise TypeError('The metrics in "%s" is not a dictionary' % test_name)
                for metric_name, metric in metrics.items():
                    if isinstance(metric, list):
                        cls._lint_aggregator_list(test_name, metric_name, metric)
                        needs_aggregation = True
                    elif isinstance(metric, dict):
                        cls._lint_configuration(test_name, metric_name, metric, parent_needing_aggregation, iteration_groups_by_config)
                    else:
                        raise TypeError('"%s" metric of "%s" was not an aggregator list or a dictionary of configurations: %s' % (metric_name, test_name, str(metric)))

            if 'tests' in test:
                cls._lint_subtest_results(test['tests'], test_name if needs_aggregation else None)
            elif needs_aggregation:
                raise TypeError('"%s" requires aggregation but "SomeTest" has no subtests' % (test_name))
        return iteration_groups_by_config

    @classmethod
    def _lint_aggregator_list(cls, test_name, metric_name, aggregator_list):
        if len(aggregator_list) != len(set(aggregator_list)):
            raise TypeError('"%s" metric of "%s" had invalid aggregator list: %s' % (metric_name, test_name, json.dumps(aggregator_list)))
        if not aggregator_list:
            raise TypeError('The aggregator list is empty in "%s" metric of "%s"' % (metric_name, test_name))
        for aggregator_name in aggregator_list:
            if cls._is_numeric(aggregator_name):
                raise TypeError('"%s" metric of "%s" is not wrapped by a configuration; e.g. "current"' % (metric_name, test_name))
            if aggregator_name not in cls.aggregators:
                raise TypeError('"%s" metric of "%s" uses unknown aggregator: %s' % (metric_name, test_name, aggregator_name))

    @classmethod
    def _lint_configuration(cls, test_name, metric_name, configurations, parent_needing_aggregation, iteration_groups_by_config):
        for config_name, values in configurations.items():
            if config_name != "current":
                raise ValueError('config name should be "current" instead of "%s"' % config_name)
            nested_list_count = [isinstance(value, list) for value in values].count(True)
            if nested_list_count not in [0, len(values)]:
                raise TypeError('"%s" metric of "%s" had malformed values: %s' % (metric_name, test_name, json.dumps(values)))

            if nested_list_count:
                value_shape = []
                for value_group in values:
                    value_shape.append(len(value_group))
                    cls._lint_values(test_name, metric_name, value_group)
            else:
                value_shape = len(values)
                cls._lint_values(test_name, metric_name, values)

            iteration_groups_by_config.setdefault(metric_name, {}).setdefault(config_name, value_shape)
            if parent_needing_aggregation and value_shape != iteration_groups_by_config[metric_name][config_name]:
                raise TypeError('"%s" metric of "%s" had a mismatching subtest values' % (metric_name, parent_needing_aggregation))

    @classmethod
    def _lint_values(cls, test_name, metric_name, values):
        if any([not cls._is_numeric(value) for value in values]):
            raise TypeError('"%s" metric of "%s" contains non-numeric value: %s' % (metric_name, test_name, json.dumps(values)))

    @classmethod
    def _is_numeric(cls, value):
        return isinstance(value, int) or isinstance(value, float)
