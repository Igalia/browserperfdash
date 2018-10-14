/**
 * Angular services for dashboard controls on index.html
 *
 * Created by tthomas@igalia.com on 01/07/17.
 */
app = angular.module('browserperfdash.dashboard.services', ['ngResource']);

app.factory('botReportsImprovementFactory', function($resource) {
    return $resource('/dash/report/improvements');
});

app.factory('botReportsRegressionFactory', function($resource) {
    return $resource('/dash/report/regressions');
});

app.factory('browserFactory', function($resource) {
    return $resource('/dash/browsers');
});

app.factory('botFullDetailsForResultsExistFactory', function($resource) {
    return $resource('/dash/bot-full-details');
});

app.factory('platformFactory', function($resource) {
    return $resource('/dash/platforms');
});

app.factory('gpuFactory', function($resource) {
    return $resource('/dash/gpus');
});

app.factory('cpuArchFactory', function($resource) {
    return $resource('/dash/cpus');
});

app.factory('testsForBrowserAndBotFactory', function ($resource) {
    return $resource('/dash/tests');
});
