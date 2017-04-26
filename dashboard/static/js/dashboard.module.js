/**
 * Angular controllers for dashboard controls on index.html
 *
 * Created by tthomas@igalia.com on 11/4/17.
 */

app = angular.module('browserperfdash.dashboard.static', ['ngResource','ngAnimate', 'ngSanitize', 'ui.bootstrap']);

app.factory('botReportsImprovementFactory', function($resource) {
    return $resource('/dash/report/improvement/:days_since/:platform/:gpu/:cpu/:browser/:test/:bot/:limit');
});

app.factory('botReportsRegressionFactory', function($resource) {
    return $resource('/dash/report/regression/:days_since/:platform/:gpu/:cpu/:browser/:test/:bot/:limit');
});

app.factory('browserFactory', function($resource) {
    return $resource('/dash/browser_results_exist');
});

app.factory('botFactory', function($resource) {
    return $resource('/dash/bot');
});

app.factory('botDetailsFactory', function ($resource) {
    return $resource('/dash/bot/detail/:bot');
});

app.factory('platformFactory', function($resource) {
    return $resource('/dash/platform');
});

app.factory('gpuFactory', function($resource) {
    return $resource('/dash/gpu');
});

app.factory('cpuArchFactory', function($resource) {
    return $resource('/dash/cpu');
});

app.factory('testFactory', function($resource) {
    return $resource('/dash/test');
});


app.controller('DeltaController', function($scope, botReportsImprovementFactory, botReportsRegressionFactory,
                                           browserFactory, botFactory, platformFactory, gpuFactory,
                                           cpuArchFactory, testFactory, botDetailsFactory,
                                           $interval, $sce, $filter) {
    $scope.browsers = browserFactory.query();
    $scope.bots = botFactory.query();
    $scope.platforms = platformFactory.query();
    $scope.gpus = gpuFactory.query();
    $scope.cpus = cpuArchFactory.query();
    $scope.tests = testFactory.query();
    $scope.botDetailsPopover = {
        templateUrl: 'bot-template.html'
    };
    $scope.prevResultDetailsPopover = {
        templateUrl: 'prev-result-template.html'
    };
    $scope.currResultDetailsPopover = {
        templateUrl: 'result-template.html'
    };
    $scope.testDetailsPopover = {
        templateUrl: 'test-template.html'
    };
    $scope.updateOtherCombos = function () {
        if ( !$scope.selectedBot ) {
            $scope.selectedPlatform = '';
            $scope.selectedCPU = '';
            $scope.selectedGPU = '';
        } else {
            $scope.selectedPlatform = $filter('filter')($scope.platforms, {'id': $scope.selectedBot.platform})[0];
            $scope.selectedCPU = $filter('filter')($scope.cpus, {'id': $scope.selectedBot.cpuArchitecture})[0];
            $scope.selectedGPU = $filter('filter')($scope.gpus, {'id': $scope.selectedBot.gpuType})[0];
        }
        $scope.reload();
    };
    $scope.reload = function () {
        $scope.noImprovementsFound = false;
        $scope.noRegressionsFound = false;
        $scope.loading = true;
        $scope.selectedDays = !$scope.selectedDays ? 5 : $scope.selectedDays;
        $scope.listLimit = !$scope.listLimit? 10 : $scope.listLimit;
        $scope.selectedBrowserId = !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.browser_id;
        $scope.selectedPlatformId = !$scope.selectedPlatform ? 'all' : $scope.selectedPlatform.id;
        $scope.selectedCPUId = !$scope.selectedCPU ? 'all' : $scope.selectedCPU.id;
        $scope.selectedGPUId = !$scope.selectedGPU ? 'all' : $scope.selectedGPU.id;
        $scope.selectedTestId = !$scope.selectedTest ? 'all' : $scope.selectedTest.id;
        $scope.selectedBotName = !$scope.selectedBot ? 'all' : $scope.selectedBot.name;
        $scope.improvement_reports = botReportsImprovementFactory.query({
            days_since: $scope.selectedDays,
            platform: $scope.selectedPlatformId,
            gpu: $scope.selectedGPUId,
            cpu: $scope.selectedCPUId,
            browser: $scope.selectedBrowserId,
            test: $scope.selectedTestId,
            bot: $scope.selectedBotName,
            limit: $scope.listLimit
        }, function (data) {
            if (data.length == 0) {
                $scope.noImprovementsFound = true;
            }
            $scope.loading_improvements = false;
        });
        $scope.regression_reports = botReportsRegressionFactory.query({
            days_since: $scope.selectedDays,
            platform: $scope.selectedPlatformId,
            gpu: $scope.selectedGPUId,
            cpu: $scope.selectedCPUId,
            browser: $scope.selectedBrowserId,
            test: $scope.selectedTestId,
            bot: $scope.selectedBotName,
            limit: $scope.listLimit
        }, function (data) {
            if (data.length == 0) {
                $scope.noRegressionsFound = true;
            }
            $scope.loading_regressions = false;
        });
        if (!$scope.loading_improvements && !$scope.loading_regressions) {
            $scope.loading = false;
        }
    };
    $scope.updateBotPopover = function (botname) {
        botDetailsFactory.get({
            bot: botname
        }, function (data) {
            $scope.bot_cpu_arch = data.cpuArchitecture;
            $scope.bot_gpu_type = data.gpuType;
            $scope.bot_platform = data.platform;
            $scope.loadedBotData = true;
        });
    };
    $scope.reload();
});
