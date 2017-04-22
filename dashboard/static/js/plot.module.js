/**
 * Angular controllers for graphs/plots used by plot.html
 *
 * Created by tthomas@igalia.com on 11/4/17.
 */
app = angular.module('browserperfdash.plot.static', ['ngResource','ngAnimate', 'ngSanitize', 'ui.bootstrap', 'angular-flot' ]);

app.factory('browserForResultExistFactory', function ($resource) {
    return $resource('/dash/browser_results_exist');
});

app.factory('botForResultsExistFactory', function($resource) {
    return $resource('/dash/bot_results_exist');
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
    return $resource('/dash/results_for_version/:browser/:root_test/:subtest/:bot');
});

app.controller('PlotController', function ($scope, browserForResultExistFactory, testForResultsExistFactory,
                                           botForResultsExistFactory, testPathFactory, testVersionOfTestFactory,
                                           testResultsForVersionFactory){
    $scope.loaded = false;
    $scope.browsers = browserForResultExistFactory.query({}, function (data) {
        $scope.selectedBrowser = data[0];
        $scope.tests = testForResultsExistFactory.query({}, function (data) {
            $scope.selectedTest = data[0];
            $scope.subtests = testPathFactory.query({
                browser: $scope.selectedBrowser.browser_id,
                root_test: $scope.selectedTest.root_test_id
            }, function (data) {
                $scope.selectedSubtest = data[0];
                $scope.testversion = testVersionOfTestFactory.query({
                    browser: $scope.selectedBrowser.browser_id,
                    root_test: $scope.selectedTest.root_test_id,
                    subtest: $scope.selectedSubtest.test_path,
                });
            });
        });
        $scope.bots = botForResultsExistFactory.query();
    });

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
    };
    $scope.drawGraph = function () {
        var datum = [];
        var results = testResultsForVersionFactory.query({
            browser: $scope.selectedBrowser.browser_id,
            root_test: $scope.selectedTest.root_test_id,
            subtest: $scope.selectedSubtest.test_path,
            bot: !$scope.selectedBot ? null : $scope.selectedBot.bot,
        }, function (data) {
            angular.forEach(data, function (value) {
                datum.push([value['timestamp']*1000, value['mean_value']]);
            });
            var mid = datum[parseInt(datum.length/2)][0];
            var end = datum[datum.length-1][0];
            var options = {
                xaxis: {
                    mode: "time",
                    tickLength: 5,
                    timeformat: "%H:%M:%S",
                }
            };
            var plot = $.plot("#placeholder", [datum], options);
            var rangeselectionCallback = function(o){
                var xaxis = plot.getAxes().xaxis;
                xaxis.options.min = o.start;
                xaxis.options.max = o.end;
                plot.setupGrid();
                plot.draw();
            };
            var overview = $.plot("#overview", [datum], {
                series: {
                    lines: {
                        show: true,
                        lineWidth: 1
                    },
                    shadowSize: 0
                },
                xaxis: {
                    ticks: 10,
                    mode: "time",
                    timeformat: "%Y-%m-%d",
                    zoomRange: [0.1, 10],
                    panRange: [-10, 10]
                },
                yaxis: {
                    ticks: [],
                    min: 0,
                    autoscaleMargin: 0.1
                },
                grid: {
                    color: "#666",
                    backgroundColor: { colors: ["#ddd", "#fff"]}
                },
                rangeselection:{
                    color: "#mar",
                    start: mid,
                    end: end,
                    enabled: true,
                    callback: rangeselectionCallback
                }
            });

            $("#placeholder").bind("plotselected", function (event, ranges) {
                // do the zooming
                $.each(plot.getXAxes(), function(_, axis) {
                    var opts = axis.options;
                    opts.min = ranges.xaxis.from;
                    opts.max = ranges.xaxis.to;
                });
                plot.setupGrid();
                plot.draw();
                plot.clearSelection();
                // don't fire event on the overview to prevent eternal loop
                overview.setSelection(ranges, true);
            });
            $("#overview").bind("plotselected", function (event, ranges) {
                plot.setSelection(ranges);
            });

            $("main-container").resizable();
            $("sub-container").resizable();

            $scope.loaded = true;

        });
    }
});

