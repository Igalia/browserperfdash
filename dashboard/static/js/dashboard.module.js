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

    $scope.updateOthers = function () {
        if ( $scope.selectedBrowser && $scope.selectedTest ) {
            $scope.updateSubtests();
        }
    }

    $scope.drawGraph = function () {
        $scope.labels = [];
        $scope.data = [];
        $scope.series = [];
        var extrainformations = {};
        var databucket = {};
        var results = testResultsForVersionFactory.query({
            browser: $scope.selectedBrowser.browser_id,
            root_test: $scope.selectedTest.root_test_id,
            subtest: $scope.selectedSubtest.test_path,
        }, function (data) {
            angular.forEach(data, function (value, key) {
                result = [];
                $scope.labels.push(value['timestamp']);
                result['yvalue'] = value['mean_value'];
                result['timestamp'] = value['timestamp'];
                result['browser_version'] = value['browser_version'];
                result['stddev'] = value['stddev'];
                result['delta'] = value['delta'];
                result['unit'] = value['unit'];
                result['test_version'] = value['test_version'];
                if(!extrainformations[value['bot']]) {
                    extrainformations[value['bot']] = {};
                    extrainformations[value['bot']][value['timestamp']] = result;
                } else {
                    extrainformations[value['bot']][value['timestamp']] = result;
                }
                if (!databucket[value['bot']]) {
                    databucket[value['bot']] = [];
                    databucket[value['bot']].push({x:value['timestamp'], y:value['mean_value']});
                } else {
                    databucket[value['bot']].push({x:value['timestamp'], y:value['mean_value']});
                }
            });
            for (var key in databucket) {
                $scope.data.push(databucket[key])
                $scope.series.push(key);
            }
        });


        $scope.options = {
            responsive: true,
            legend: {
                display: true,
            },
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: $scope.testversion[0]['metrics']['metric'] +
                        ' (' +  ($scope.testversion[0]['metrics']['metric'] == 'up' ? 'up' : 'down') + ' is better)'
                    }
                }],
                xAxes: [{
                    type: 'linear',
                    position: 'bottom',
                    ticks: {
                        callback: function (value, index, values) {
                            return moment.unix(parseInt(value)).format('YYYY-MM-DD')
                        }
                    }
                }]
            },
            tooltips: {
                enabled: true,
                mode: 'single',
                callbacks: {
                    title: function (tooltipItem, data) {
                        return $scope.selectedBrowser.browser_id + "@" + data.datasets[tooltipItem[0].datasetIndex].label;
                    },
                    label: function(tooltipItem, data) {
                        currentbot = data.datasets[tooltipItem.datasetIndex].label;
                        var label = extrainformations[currentbot][tooltipItem.xLabel]['timestamp'];
                        var datasetLabel = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                        return [
                            "Time: " + moment.unix(parseInt(label)).format('YYYY-MM-DD, HH:mm:ss'),
                            "Test Version: " + extrainformations[currentbot][tooltipItem.xLabel]['test_version'].slice(-7),
                            "Browser Version: " + extrainformations[currentbot][tooltipItem.xLabel]['browser_version'],
                            "Std. Dev: " + parseFloat(extrainformations[currentbot][tooltipItem.xLabel]['stddev']).toFixed(3),
                            "Value: " + parseFloat(datasetLabel.y).toFixed(3) + ' ' +  extrainformations[currentbot][tooltipItem.xLabel]['unit'],
                            "Delta: " + parseFloat(extrainformations[currentbot][tooltipItem.xLabel]['delta']).toFixed(3) + " %",
                        ];
                    }
                }
            }
        };
        //
        // $scope.onClick = function (points, evt) {
        //     console.log(points, evt);
        // };
    };


});

