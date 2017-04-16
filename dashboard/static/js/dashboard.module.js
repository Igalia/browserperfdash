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
    $scope.populateMetrics = function (data) {
        $scope.mean_value_string = "";
        $scope.mean_prev_value_string = "";
        prefixArray = [];
        angular.forEach(data.metric_unit.prefix, function(key, value) {
            prefixArray.push({
                symbol: key,
                unit: value
            });
        });
        var sortedPrefixArray = $filter('orderBy')(prefixArray, 'unit');
        var mean_value = data.mean_value;
        var prev_mean_value = !data.prev_results.mean_value ? null : data.prev_results.mean_value;
        var prefixArrayLen = sortedPrefixArray.length;
        calculatePrefix(mean_value, sortedPrefixArray, sortedPrefixArray.length, data.metric_unit.unit);
        calculatePreviousPrefix(prev_mean_value, sortedPrefixArray, sortedPrefixArray.length, data.metric_unit.unit);
        return { 'mean': $scope.mean_value_string, 'prev_mean' : $scope.mean_prev_value_string };
    };

    var calculatePrefix = function (mean_value, prefixArray, original_length, original_prefix) {
        var prefixArrayLen = prefixArray.length;
        for (var i=0; i < prefixArrayLen ; i++) {
            if ( prefixArrayLen == 1 && prefixArrayLen != original_length ) {
                $scope.mean_value_string += parseFloat(mean_value).toFixed(2) + " " + original_prefix + " ";
                return;
            }
            var restPrefixArray = prefixArray.slice(i + 1, prefixArrayLen);
            var mean_factor = mean_value / prefixArray[i]['symbol'];
            var mean_factor_floored = Math.floor(mean_factor);
            if ( mean_factor_floored > 0 ) {
                mean_value = (mean_factor - mean_factor_floored) * prefixArray[i]['symbol'];
                $scope.mean_value_string += mean_factor_floored + " " + prefixArray[i]['unit'] + " ";
            }
            return calculatePrefix(mean_value, restPrefixArray, original_length, original_prefix);
        }
    };
    var calculatePreviousPrefix = function (mean_value, prefixArray, original_length, original_prefix) {
        var prefixArrayLen = prefixArray.length;
        for (var i=0; i < prefixArrayLen ; i++) {
            if ( prefixArrayLen == 1 && prefixArrayLen != original_length ) {
                $scope.mean_prev_value_string += parseFloat(mean_value).toFixed(2) + " " + original_prefix + " ";
                return;
            }
            var restPrefixArray = prefixArray.slice(i + 1, prefixArrayLen);
            var mean_factor = mean_value / prefixArray[i]['symbol'];
            var mean_factor_floored = Math.floor(mean_factor);
            if ( mean_factor_floored > 0 ) {
                mean_value = (mean_factor - mean_factor_floored) * prefixArray[i]['symbol'];
                $scope.mean_prev_value_string += mean_factor_floored + " " + prefixArray[i]['unit'] + " ";
            }
            return calculatePreviousPrefix(mean_value, restPrefixArray, original_length, original_prefix);
        }
    };
    $scope.reload();
});
