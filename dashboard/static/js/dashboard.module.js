app = angular.module('browserperfdash.dashboard.static', ['ngResource','ngAnimate', 'ui.bootstrap']);

app.factory('botReportsFactory', function($resource) {
    return $resource('/dash/report');
});

app.factory('browserFactory', function($resource) {
    return $resource('/dash/browser');
});

app.factory('botFactory', function($resource) {
    return $resource('/dash/bot');
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
    $scope.htmlToolTip = $sce.trustAsHtml("<div> hello </div>");
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

