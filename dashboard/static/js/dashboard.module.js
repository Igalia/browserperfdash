app = angular.module('browserperfdash.dashboard.static', ['ngResource']);

app.factory('botReportsFactory', function($resource) {
  return $resource('/dash/result');
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

app.controller('AppController', function($scope, botReportsFactory, browserFactory,
                                         botFactory, platformFactory, gpuFactory,
                                         cpuArchFactory, $interval) {
    $scope.browsers = browserFactory.query();
    $scope.bots = botFactory.query();
    $scope.platforms = platformFactory.query();
    $scope.gpus = gpuFactory.query();
    $scope.cpus = cpuArchFactory.query();
    $scope.updateOtherCombos = function () {
        if ( $scope.selectedBot ) {
            $scope.selectedPlatform = $scope.selectedBot.platform;
            $scope.selectedCPU = $scope.selectedBot.cpu;
            $scope.selectedGPU = $scope.selectedBot.gpu;
        }
    };
    $scope.reload = function () {
        $scope.reports = botReportsFactory.query();
    };
    $scope.reload();
});