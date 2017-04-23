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
    return $resource('/dash/bot_results_exist/:browser');
});

app.factory('testsForBrowserAndBotFactory', function ($resource) {
    return $resource('/dash/tests_for_browser_bot/:browser/:bot');
});

app.factory('testPathFactory', function ($resource) {
    return $resource('/dash/testpath/:browser/:root_test');
});

app.factory('testMetricsOfTestAndSubtestFactory', function ($resource) {
    return $resource('/dash/test_metrics/:root_test/:subtest');
});

app.factory('testResultsForTestAndSubtestFactory', function ($resource) {
    return $resource('/dash/results_for_subtest/:browser/:root_test/:subtest/:bot');
});

app.controller('PlotController', function ($scope, browserForResultExistFactory, botForResultsExistFactory, testPathFactory,
                                           testMetricsOfTestAndSubtestFactory, testResultsForTestAndSubtestFactory,
                                           testsForBrowserAndBotFactory, $filter){
    $scope.loaded = false;
    $scope.loading = false;
    $scope.disableSubtest = false;
    $scope.disableTest = false;
    $scope.disableBrowser = false;
    $scope.disableBot = false;

    $scope.onBrowserChange = function (selectedBrowser) {
        //Update tests
        $scope.tests = testsForBrowserAndBotFactory.query({
            browser: !selectedBrowser ? $scope.selectedBrowser.browser_id : selectedBrowser.browser_id,
            bot: !$scope.selectedBot ? null : $scope.selectedBot.bot,
        }, function () {
            $scope.selectedTest = $scope.tests[0];
            $scope.onTestsChange();
            $scope.bots = botForResultsExistFactory.query({
                browser: $scope.selectedBrowser.browser_id
            });
        });
    };

    $scope.onBotsChange = function () {
        $scope.tests = testsForBrowserAndBotFactory.query({
            browser: $scope.selectedBrowser.browser_id,
            bot: !$scope.selectedBot ? null : $scope.selectedBot.bot,
        }, function (data) {
            if(data.length === 0) {
                $scope.selectedTest = [];
                $scope.selectedSubtest = [];
                $scope.disableTest = true;
                $scope.disableSubtest = true;
            } else {
                $scope.disableTest = false;
                $scope.disableSubtest = false;
                $scope.selectedTest = $scope.tests[0];
            }
        });
    };

    $scope.onTestsChange = function () {
        if(!$scope.selectedTest) {
            return;
        }
        $scope.subtests = testPathFactory.query({
            browser: $scope.selectedBrowser.browser_id,
            root_test: $scope.selectedTest.root_test.id
        }, function (data) {
            $scope.selectedSubtest = $scope.subtests[0];
        });
    };

    $scope.browsers = browserForResultExistFactory.query({}, function (data) {
        if(data.length === 0) {
            $scope.selectedTest = [];
            $scope.selectedSubtest = [];
            $scope.selectedBrowser = [];
            $scope.selectedBot = [];
            $scope.disableBot = true;
            $scope.disableBrowser = true;
            $scope.disableTest = true;
            $scope.disableSubtest = true;
        }
        $scope.selectedBrowser =  $scope.browsers[0];
        $scope.onBrowserChange($scope.selectedBrowser);
    });

    $scope.drawGraph = function () {
        $scope.testMetrics = testMetricsOfTestAndSubtestFactory.query({
            root_test: $scope.selectedTest.root_test.id,
            subtest: $scope.selectedSubtest.test_path,
        });
        $scope.loading = true;
        var datum = [];
        var results = testResultsForTestAndSubtestFactory.query({
            browser: $scope.selectedBrowser.browser_id,
            root_test: $scope.selectedTest.root_test.id,
            subtest: $scope.selectedSubtest.test_path,
            bot: !$scope.selectedBot ? null : $scope.selectedBot.bot,
        }, function (data) {
            // Need to update tooltips, etc
            $scope.currentBrowser = $scope.selectedBrowser.browser_id;
            $scope.currentSubtestPath = $scope.selectedSubtest.test_path;

            extraToolTipInfo = {};

            var placeholder = $("#placeholder");
            var overview_placeholder = $("#overview");

            angular.forEach(data, function (value) {
                tooltipData = {};
                jqueryTimestamp = value['timestamp']*1000;
                datum.push([jqueryTimestamp, value['mean_value']]);
                tooltipData['yvalue'] = value['mean_value'];
                tooltipData['browser_version'] = value['browser_version'];
                tooltipData['stddev'] = value['stddev'];
                tooltipData['delta'] = value['delta'];
                tooltipData['test_version'] = value['test_version'];
                extraToolTipInfo[jqueryTimestamp] = tooltipData;
            });

            // Will need it for selection on overview chart
            var mid = datum[parseInt(datum.length/2)][0];
            var end = datum[datum.length-1][0];
            var plot = $.plot(placeholder, [datum], {
                xaxis: {
                    mode: "time",
                    tickLength: 5,
                    timeformat: "%H:%M:%S",
                },
                crosshair: {
                    mode: "x,y"
                },
                yaxis: {
                    axisLabel : $scope.testMetrics[0]['metric_unit']['name'] + ' (' +
                    ($scope.testMetrics[0]['metric_unit']['is_better'] == 'up' ? 'up' : 'down') + ' is better)',
                    position: 'left',
                },
                grid: {
                    hoverable: true,
                    clickable: true
                },
            });
            var overview = $.plot(overview_placeholder, [datum], {
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
                    autoscaleMargin: 0.1,
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
                    callback: function(o){
                        var xaxis = plot.getAxes().xaxis;
                        xaxis.options.min = o.start;
                        xaxis.options.max = o.end;
                        plot.setupGrid();
                        plot.draw();
                    }
                }
            });
            $("<div id='tooltip'></div>").css({
                position: "absolute",
                display: "none",
                border: "1px solid #fdd",
                padding: "2px",
                "background-color": "#fee",
                opacity: 0.95
            }).appendTo("body");

            placeholder.bind("plothover", function (event, pos, item) {
                if(item) {
                    var x = item.datapoint[0], y = item.datapoint[1];
                    var date = new Date(x);
                    $("#tooltip").html( $scope.currentBrowser + "@<i>" + $scope.currentSubtestPath + "</i><br>"
                        + "<b>Time</b>: " +  date.toISOString().split('T')[0] + ", " + date.toISOString().split('T')[1].substring(0,8)+ "<br>"
                        + "<b>Test Version</b>: " + extraToolTipInfo[x]['test_version'].slice(-7) + "<br>"
                        + "<b>Browser Version</b>: " + extraToolTipInfo[x]['browser_version'] + "<br>"
                        + "<b>Std. Dev</b>: " + parseFloat(extraToolTipInfo[x]['stddev']).toFixed(3) + "<br>"
                        + "<b>Value</b>: " +  parseFloat(y).toFixed(3) + " " + $scope.testMetrics[0]['metric_unit']['unit'] + "<br>"
                        + "<b>Delta</b> :" +  parseFloat(extraToolTipInfo[x]['delta']).toFixed(3) + "<br>"
                        + "<b>Aggregation </b> :" + $scope.selectedSubtest.aggregation + "<br>")
                        .css({top: item.pageY+5, left: item.pageX+5})
                        .fadeIn(200);
                } else {
                    $("#tooltip").hide();
                }
            });
            placeholder.bind("plotclick", function (event, pos, item) {
                if (item) {
                    plot.highlight(item.series, item.datapoint);
                }
            });

            placeholder.bind("plotselected", function (event, ranges) {
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
            overview_placeholder.bind("plotselected", function (event, ranges) {
                plot.setSelection(ranges);
            });

            $("main-container").resizable();
            $("sub-container").resizable();
            $scope.loading = false;
            $scope.loaded = true;
        });
    }
});

