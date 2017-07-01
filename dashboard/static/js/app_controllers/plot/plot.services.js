/**
 * Angular services for graphs/plots used by plot.html
 *
 * Created by tthomas@igalia.com on 01/07/17.
 */
app = angular.module('browserperfdash.plot.services', ['ngResource']);

app.factory('browserForResultExistFactory', function ($resource) {
    return $resource('/dash/browser_results_exist');
});

app.factory('botForResultsExistFactory', function($resource) {
    return $resource('/dash/bot_results_exist/:browser');
});

app.factory('testsForBrowserAndBotFactory', function ($resource) {
    return $resource('/dash/tests_for_browser_bot/:browser/:bot');
});

app.factory('subTestPathFactory', function ($resource) {
    return $resource('/dash/testpath/:browser/:root_test');
});

app.factory('testMetricsOfTestAndSubtestFactory', function ($resource) {
    return $resource('/dash/test_metrics/:root_test/:subtest');
});

app.factory('testResultsForTestAndSubtestFactory', function ($resource) {
    return $resource('/dash/results_for_subtest/:browser/:root_test/:bot/:subtest/');
});
