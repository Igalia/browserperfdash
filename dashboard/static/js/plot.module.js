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
    $scope.loading = false;
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
        $scope.loading = true;
        var datum = [];
        var extraToolTipInfo = {};
        var results = testResultsForVersionFactory.query({
            browser: $scope.selectedBrowser.browser_id,
            root_test: $scope.selectedTest.root_test_id,
            subtest: $scope.selectedSubtest.test_path,
            bot: !$scope.selectedBot ? null : $scope.selectedBot.bot,
        }, function (data) {
            var placeholder = $("#placeholder");
            var overview = $("#overview");
            angular.forEach(data, function (value) {
                tooltipData = {};
                jqueryTimestamp = value['timestamp']*1000;
                datum.push([jqueryTimestamp, value['mean_value']]);
                tooltipData['yvalue'] = value['mean_value'];
                tooltipData['browser_version'] = value['browser_version'];
                tooltipData['stddev'] = value['stddev'];
                tooltipData['delta'] = value['delta'];
                tooltipData['unit'] = value['unit'];
                tooltipData['test_version'] = value['test_version'];
                extraToolTipInfo[jqueryTimestamp] = tooltipData;
            });
            var mid = datum[parseInt(datum.length/2)][0];
            var end = datum[datum.length-1][0];
            var options = {
                xaxis: {
                    mode: "time",
                    tickLength: 5,
                    timeformat: "%H:%M:%S",
                },
                crosshair: {
                    mode: "x,y"
                },
                grid: {
                    hoverable: true,
                    clickable: true
                }
            };
            placeholder.show();
            var plot = $.plot(placeholder, [datum], options);
            var rangeselectionCallback = function(o){
                var xaxis = plot.getAxes().xaxis;
                xaxis.options.min = o.start;
                xaxis.options.max = o.end;
                plot.setupGrid();
                plot.draw();
            };
            var overview = $.plot(overview, [datum], {
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
            $("<div id='tooltip'></div>").css({
                position: "absolute",
                display: "none",
                border: "1px solid #fdd",
                padding: "2px",
                "background-color": "#fee",
                opacity: 0.80
            }).appendTo("body");

            placeholder.bind("plothover", function (event, pos, item) {
                if(item) {
                    var x = item.datapoint[0], y = item.datapoint[1];
                    var date = new Date(x);
                    $("#tooltip").html( $scope.selectedBrowser.browser_id + "@<i>" + $scope.selectedSubtest.test_path + "</i><br>"
                        + "<b>Time</b>: " +  date.toISOString().split('T')[0] + ", " + date.toISOString().split('T')[1].substring(0,8)+ "<br>"
                        + "<b>Test Version</b>: " + extraToolTipInfo[x]['test_version'].slice(-7) + "<br>"
                        + "<b>Browser Version</b>: " + extraToolTipInfo[x]['browser_version'] + "<br>"
                        + "<b>Std. Dev</b>: " + parseFloat(extraToolTipInfo[x]['stddev']).toFixed(3) + "<br>"
                        + "<b>Value</b>: " +  parseFloat(y).toFixed(3) + " " + extraToolTipInfo[x]['unit'] + "<br>"
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
            $("#overview").bind("plotselected", function (event, ranges) {
                plot.setSelection(ranges);
            });

            $("main-container").resizable();
            $("sub-container").resizable();
            $scope.loading = false;
            $scope.loaded = true;
        });
    }
});

