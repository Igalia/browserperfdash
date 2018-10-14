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
    return $resource('/dash/browser_results_exist');
});

app.factory('botFullDetailsForResultsExistFactory', function($resource) {
    return $resource('/dash/bot_full_details_for_exist/:browser');
});

app.factory('platformFactory', function($resource) {
    return $resource('/dash/platform_results_exist');
});

app.factory('gpuFactory', function($resource) {
    return $resource('/dash/gpu_results_exist');
});

app.factory('cpuArchFactory', function($resource) {
    return $resource('/dash/cpu_results_exist');
});

app.factory('testsForBrowserAndBotFactory', function ($resource) {
    return $resource('/dash/tests_for_browser_bot/:browser/:bot');
});
