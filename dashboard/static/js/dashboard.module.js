/**
 * Angular controllers for dashboard controls on index.html
 *
 * Created by tthomas@igalia.com on 11/4/17.
 */

app = angular.module('browserperfdash.dashboard.static', ['ngResource','ngAnimate', 'ngSanitize', 'ui.bootstrap']);

app.factory('botReportsFactory', function($resource) {
    return $resource('/dash/report/:days_since/:platform/:gpu/:cpu');
});

app.factory('browserFactory', function($resource) {
    return $resource('/dash/browser');
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


app.controller('DeltaController', function($scope, botReportsFactory, browserFactory,
                                           botFactory, platformFactory, gpuFactory,
                                           cpuArchFactory, testFactory, botDetailsFactory,
                                           $interval, $sce) {
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
    $scope.selectedDays = !$scope.selectedDays ? 5 : $scope.selectedDays;
    $scope.selectedPlatform = !$scope.selectedPlatform ? 'all' : $scope.selectedPlatform;
    $scope.selectedCPU = !$scope.selectedCPU ? 'all' : $scope.selectedCPU;
    $scope.selectedGPU = !$scope.selectedGPU ? 'all' : $scope.selectedGPU;
    $scope.reload = function () {
        $scope.loading = true;
        $scope.reports = botReportsFactory.query({
            days_since: $scope.selectedDays,
            platform: $scope.selectedPlatform,
            gpu: $scope.selectedGPU,
            cpu: $scope.selectedCPU
        }, function () {
            $scope.loading = false;
        });
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
