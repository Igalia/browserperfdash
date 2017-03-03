app = angular.module('browserperfdash.dashboard.static', ['ngResource','ngAnimate', 'ngSanitize', 'ui.bootstrap',
    'chart.js' ]);

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

app.factory('testResultsForVersionFactory', function ($resource) {
    return $resource('/dash/results_for_version/:browser/:root_test/:subtest');
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
                                           botForResultsExistFactory, testPathFactory, testVersionOfTestFactory,
                                           testResultsForVersionFactory) {
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
    };
    $scope.drawGraph = function () {
        $scope.data = [[]];
        $scope.labels = [];
        var extrainformations = [];
        $scope.series = [$scope.selectedSubtest.test_path];
        var results = testResultsForVersionFactory.query({
            browser: $scope.selectedBrowser.browser_id,
            root_test: $scope.selectedTest.root_test_id,
            subtest: $scope.selectedSubtest.test_path,
        }, function (data) {
            angular.forEach(data, function (value, key) {
                result = [];
                $scope.data[0].push(value['mean_value']);
                var recvdate = new Date(value['timestamp']);
                $scope.labels.push(recvdate.toDateString());
                result['originalTimestamps'] = recvdate;
                result['browser_version'] = value['browser_version'];
                result['stddev'] = value['stddev'];
                extrainformations.push(result);
            })
        });
        $scope.options = {
            legend: {
                display: true,
            },
            tooltips: {
                enabled: true,
                mode: 'single',
                callbacks: {
                    label: function(tooltipItem, data) {
                        var label = extrainformations[tooltipItem.index]['originalTimestamps'].toISOString().slice(0,19);
                        var datasetLabel = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                        return [
                            "Time: " + label,
                            "Browser Version: " + extrainformations[tooltipItem.index]['browser_version'],
                            "Std. Dev: " + extrainformations[tooltipItem.index]['stddev'],
                            "Value: " + datasetLabel + '%'
                        ];
                    }
                }
            },
        };

        $scope.onClick = function (points, evt) {
            console.log(points, evt);
        };
    };


});

