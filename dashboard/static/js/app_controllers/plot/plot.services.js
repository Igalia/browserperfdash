/**
 * Angular services for graphs/plots used by plot.html
 *
 * Created by tthomas@igalia.com on 01/07/17.
 */
app = angular.module('browserperfdash.plot.services', ['ngResource']);

app.factory('browserForResultExistFactory', function ($resource) {
    return $resource('/dash/browsers');
});

app.factory('botForResultsExistFactory', function($resource) {
    return $resource('/dash/bots');
});

app.factory('testsForBrowserAndBotFactory', function ($resource) {
    return $resource('/dash/tests');
});

app.factory('subTestPathFactory', function ($resource) {
    return $resource('/dash/test-paths');
});

app.factory('testMetricsOfTestAndSubtestFactory', function ($resource) {
    return $resource('/dash/test-metrics/:root_test/:subtest');
});

app.factory('testResultsForTestAndSubtestFactory', function ($resource) {
    return $resource('/dash/results');
});
