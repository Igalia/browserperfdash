app = angular.module('browserperfdash.dashboard.static', ['ngResource','ngAnimate', 'ngSanitize', 'ui.bootstrap']);

app.factory('botReportsFactory', function($resource) {
    return $resource('/dash/report');
});

app.factory('browserFactory', function($resource) {
    return $resource('/dash/browser');
});

app.factory('browserForResultExistFactory', function ($resource) {
    return $resource('/dash/browser_results_exist');
});

app.factory('botFactory', function($resource) {
    return $resource('/dash/bot');
});

app.factory('botForResultsExistFactory', function($resource) {
    return $resource('/dash/bot_results_exist');
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

app.factory('testForResultsExistFactory', function($resource) {
    return $resource('/dash/test_results_exist');
});

app.factory('testPathFactory', function ($resource) {
    return $resource('/dash/testpath/:browser/:root_test');
});

app.factory('testVersionOfTestFactory', function ($resource) {
    return $resource('/dash/test_version/:browser/:root_test/:subtest');
});

app.controller('AppController', function($scope, botReportsFactory, browserFactory,
                                         botFactory, platformFactory, gpuFactory,
                                         cpuArchFactory, testFactory,  $interval) {
    $scope.browsers = browserFactory.query();
    $scope.bots = botFactory.query();
    $scope.platforms = platformFactory.query();
    $scope.gpus = gpuFactory.query();
    $scope.cpus = cpuArchFactory.query();
    $scope.tests = testFactory.query();
    $scope.updateOtherCombos = function () {
        if ( !$scope.selectedBot ) {
            $scope.selectedPlatform = '';
            $scope.selectedCPU = '';
            $scope.selectedGPU = '';
        } else {
            $scope.selectedPlatform = $scope.selectedBot.platform;
            $scope.selectedCPU = $scope.selectedBot.cpuArchitecture;
            $scope.selectedGPU = $scope.selectedBot.gpuType;
        }
    };
    $scope.reload = function () {
        $scope.reports = botReportsFactory.query();
    };
    $scope.reload();
});

app.controller('DeltaController', function($scope, botReportsFactory, browserFactory,
                                           botFactory, platformFactory, gpuFactory,
                                           cpuArchFactory, testFactory, $interval, $sce) {
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
            $scope.selectedPlatform = $scope.selectedBot.platform;
            $scope.selectedCPU = $scope.selectedBot.cpuArchitecture;
            $scope.selectedGPU = $scope.selectedBot.gpuType;
        }
    };
    $scope.reload = function () {
        $scope.reports = botReportsFactory.query();
    };
    $scope.reload();
});

app.controller('PlotController', function ($scope, browserForResultExistFactory, testForResultsExistFactory,
                                           botForResultsExistFactory, testPathFactory, testVersionOfTestFactory) {
    $scope.browsers = browserForResultExistFactory.query();
    $scope.tests = testForResultsExistFactory.query();
    $scope.bots = botForResultsExistFactory.query();
    $scope.updateSubtests = function () {
        if ( $scope.selectedBrowser != undefined ) {
            $scope.subtests = testPathFactory.query({
                browser: $scope.selectedBrowser.browser_id,
                root_test: $scope.selectedTest.root_test_id
            });
        }
    };
    $scope.updateVersions = function () {
        if ( $scope.selectedSubtest != undefined ) {
            $scope.testversion = testVersionOfTestFactory.query({
                browser: $scope.selectedBrowser.browser_id,
                root_test: $scope.selectedTest.root_test_id,
                subtest: $scope.selectedSubtest.test_path,
            });
        }
    }
});

