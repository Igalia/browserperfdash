/**
 * Angular controllers for graphs/plots used by plot.html
 *
 * Created by tthomas@igalia.com on 11/4/17.
 */
app = angular.module('browserperfdash.plot.static', ['ngResource','ngAnimate', 'ngSanitize', 'angular-flot']);

app.factory('browserForResultExistFactory', function ($resource) {
    return $resource('/dash/browser_results_exist');
});

app.factory('botForResultsExistFactory', function($resource) {
    return $resource('/dash/bot_results_exist/:browser');
});

app.factory('testsForBrowserAndBotFactory', function ($resource) {
    return $resource('/dash/tests_for_browser_bot/:browser/:bot');
});

app.factory('subTestPathFactory', function ($resource) {
    return $resource('/dash/testpath/:browser/:root_test');
});

app.factory('testMetricsOfTestAndSubtestFactory', function ($resource) {
    return $resource('/dash/test_metrics/:root_test/:subtest');
});

app.factory('testResultsForTestAndSubtestFactory', function ($resource) {
    return $resource('/dash/results_for_subtest/:browser/:root_test/:bot/:subtest/');
});

app.controller('PlotController', function ($scope, browserForResultExistFactory, botForResultsExistFactory, subTestPathFactory,
                                           testMetricsOfTestAndSubtestFactory, testResultsForTestAndSubtestFactory,
                                           testsForBrowserAndBotFactory, $filter, $location){
    $scope.graphCounter = 0;
    $scope.drawnsequences = [];
    var extraToolTipInfo = new Array(new Array());
    $scope.drawnTestsDetails = new Array(new Array());
    $scope.plots = [];

    $scope.loaded = false;
    $scope.loading = false;
    $scope.disableSubtest = false;
    $scope.disableTest = false;
    $scope.disableBrowser = false;
    $scope.disableBot = false;
    $scope.buttonHide = false;

    $scope.onBrowserChange = function () {
        //Update tests
        $scope.tests = testsForBrowserAndBotFactory.query({
            browser: !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.id,
            bot: !$scope.selectedBot ? null : $scope.selectedBot.name,
        }, function () {
            $scope.selectedTest = $scope.tests[0];
            $scope.onTestsChange();
            $scope.bots = botForResultsExistFactory.query({
                browser: !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.id
            });
        });
    };

    $scope.onBotsChange = function () {
        $scope.tests = testsForBrowserAndBotFactory.query({
            browser: !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.id,
            bot: !$scope.selectedBot ? null : $scope.selectedBot.name,
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
                $scope.onTestsChange();
            }
        });
    };

    $scope.onTestsChange = function () {
        if(!$scope.selectedTest) {
            return;
        }
        $scope.subtests = subTestPathFactory.query({
            browser: !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.id,
            root_test: $scope.selectedTest.root_test.id
        }, function (data) {
            // We might have something here due to URL data
            if (!$scope.selectedSubtest) { $scope.selectedSubtest = data[0]; }
        });
    };

    if( $location.$$path === "" ) {
        $scope.browsers = browserForResultExistFactory.query({}, function (data) {
            if (data.length === 0) {
                $scope.selectedTest = [];
                $scope.selectedSubtest = [];
                $scope.selectedBrowser = [];
                $scope.selectedBot = [];
                $scope.disableBot = true;
                $scope.disableBrowser = true;
                $scope.disableTest = true;
                $scope.disableSubtest = true;
                $scope.buttonHide = true;
                return;
            }
            $scope.onBrowserChange();
        });
    } else {
        // Just load browsers, bots, tests and subtest with rand
        $scope.browsers = browserForResultExistFactory.query();
        $scope.bots = botForResultsExistFactory.query({
            browser: 'all'
        });
        $scope.tests = testsForBrowserAndBotFactory.query({
            browser: 'all',
            bot: null
        });

        //Lets just wait for everything to load, and then think about populating things
        $scope.browsers.$promise.then(function () {
            $scope.tests.$promise.then(function () {
                $scope.bots.$promise.then(function () {
                    var unsortedPlotArray = JSON.parse(atob(decodeURIComponent($location.$$path.substr(1))));
                    var sortedPlotArray = $filter('orderBy')(unsortedPlotArray, '-seq');
                    for ( var i=0; i< sortedPlotArray.length; i++ ) {
                        var value = sortedPlotArray[i];
                        var subtests = subTestPathFactory.query({
                            browser: value['browser'],
                            root_test: value['root_test']
                        });

                        $scope.drawGraph(value['browser'], value['bot'], value['root_test'], value['subtest'],
                            value['seq'], value['start'], value['end'], value['plots'], subtests, function (plotnumberdrawn) {
                                $scope.drawnsequences.push(plotnumberdrawn);
                            });
                    }

                    var checkIfEverThingDrawn = setInterval(function () {
                        if($scope.drawnsequences.length === sortedPlotArray.length) {
                            reorderGraphs($scope.drawnsequences.length);
                            clearInterval(checkIfEverThingDrawn);
                        }
                    }, 500);
                });
            });
        });
    }

    $scope.drawGraph = function (browser_inc, bot_inc, root_test_inc, subtest_inc, seq, start_inc, end_inc, plots_inc, subtests,
                                 callbackondone) {
        // Update tooltips, etc
        var currentBrowser = !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.id,
            selectedTest = $scope.selectedTest, selectedSubtest = $scope.selectedSubtest,
            selectedBrowser = $scope.selectedBrowser, selectedBot = $scope.selectedBot, selectionstart, selectionend;

        $scope.plotsinGraph = {};

        /* Check if args were present. If yes, we need to modify drop-down selections and plot */
        if (browser_inc) {
            selectedBrowser = $filter('filter')($scope.browsers, {'id': browser_inc})[0];
            $scope.selectedBrowser = selectedBrowser;
            currentBrowser = browser_inc;
        }
        if (bot_inc) {
            selectedBot = $filter('filter')($scope.bots, {'name': bot_inc})[0];
        }
        if (root_test_inc) {
            selectedTest = $filter('filter')($scope.tests, function (value, index, array) {
                if (value['root_test']['id'] === root_test_inc) {
                    return array[index];
                }
            })[0];
        }

        var currentSubtestPath = !subtest_inc ? selectedSubtest.test_path : subtest_inc;

        if (!subtests) { subtests = $scope.subtests; }

        subtests.$promise.then(function () {
            $scope.subtests = subtests;

            if (subtest_inc) {
                selectedSubtest = $filter('filter')(subtests, {'test_path': subtest_inc})[0];
            }

            // Modify dropdown selections manually
            $scope.selectedTest = selectedTest;
            $scope.selectedSubtest = selectedSubtest;

            testMetricsOfTestAndSubtestFactory.query({
                root_test: selectedTest.root_test.id,
                subtest: encodeURIComponent(selectedSubtest.test_path),
            }, function (testMetrics) {
                $scope.loading = true;
                testResultsForTestAndSubtestFactory.query({
                    browser: !selectedBrowser ? 'all' : selectedBrowser.id,
                    root_test: selectedTest.root_test.id,
                    bot: !selectedBot ? 'all' : selectedBot.name,
                    subtest: encodeURIComponent(selectedSubtest.test_path)
                }, function (results) {
                    if (seq !== undefined) {
                        // This is a draw from the URL - lets use the original sequence for this graph
                        $scope.graphCounter = seq;
                    } else if ($scope.drawnsequences.length > 1) {
                        // If there is existing graphs, and this is a new added graph
                        $scope.graphCounter = $scope.drawnsequences.length;
                    }

                    extraToolTipInfo[$scope.graphCounter] = {};
                    botReportData = {};

                    angular.forEach(results, function (value) {

                        dictkey = value['browser'] + "@" + value['bot'];
                        extraToolTipInfo[$scope.graphCounter][dictkey] = !extraToolTipInfo[$scope.graphCounter][dictkey] ? {} :
                            extraToolTipInfo[$scope.graphCounter][dictkey];
                        botReportData[dictkey] = !botReportData[dictkey] ? [] : botReportData[dictkey];

                        // Data to draw plots
                        jqueryTimestamp = value['timestamp'] * 1000;
                        botReportData[dictkey].push([jqueryTimestamp, value['mean_value']]);

                        // Data to populate tooltips
                        tooltipData = {};
                        tooltipData['yvalue'] = value['mean_value'];
                        tooltipData['browser'] = value['browser'];
                        tooltipData['browser_version'] = value['browser_version'];
                        tooltipData['stddev'] = value['stddev'];
                        tooltipData['delta'] = value['delta'];
                        tooltipData['test_version'] = value['test_version'];

                        extraToolTipInfo[$scope.graphCounter][dictkey][jqueryTimestamp] = tooltipData;
                    });

                    $scope.drawnTestsDetails[$scope.graphCounter] = {};
                    testDetails = {};
                    testDetails['root_test'] = selectedTest.root_test.id;
                    testDetails['sub_test'] = currentSubtestPath;
                    testDetails['browser'] = currentBrowser;
                    $scope.drawnTestsDetails[$scope.graphCounter] = testDetails;


                    var subcontainer = $('<div>').addClass("sub-container").append(
                        $('<div>').addClass("overview")
                    );
                    var maincontainer = $('<div>').addClass("main-container").append(
                        $('<div>').addClass("placeholder").attr('id', $scope.graphCounter)
                    );

                    var newRow = $('<div>').addClass('row').append(
                        $('<div>').addClass('col-md-9').append(
                            maincontainer, subcontainer
                        ),
                        $('<div>').addClass('col-md-3').attr('ng-show', 'loaded').append(
                            "<div class='panel panel-default'>" +
                            "<div class='panel-heading'><h3 class='panel-title' id=" + $scope.graphCounter + ">" +
                            "Test: " + selectedTest.root_test.id + "</h3></div>" +
                            "<div class='panel-body' id=" + $scope.graphCounter + ">" +
                            "Subtest: " + currentSubtestPath + "<br>" +
                            "Browser: " + currentBrowser + "<br>" +
                            "<span class='choices' id=choice-" + $scope.graphCounter + "></span></div></div>"
                        )
                    ).css('padding-top', '10px');
                    var infoRow = $('<div>').addClass('row').append(
                        "<span><b>" + $scope.drawnTestsDetails[$scope.graphCounter]['browser'] + "</b>@" +
                        $scope.drawnTestsDetails[$scope.graphCounter]['root_test'] + "/" +
                        $scope.drawnTestsDetails[$scope.graphCounter]['sub_test'] + "</span>" +
                        "<button type='button' class='close' aria-label='Close'><span aria-hidden='true' " +
                        "class='close_button'>&times;</span></button>"
                    ).css('text-align', 'center').attr('ng-show', 'loaded');

                    if (seq !== undefined){
                        var dummyrow = $('<div>').addClass('dummy').attr('id', seq).append(infoRow, newRow);
                    } else {
                        var dummyrow = $('<div>').addClass('dummy').attr('id', $scope.graphCounter).append(infoRow, newRow);
                    }

                    var topRow = $('div#plot_area>.dummy:first');
                    if (!topRow.length) {
                        //Looks like the first plot was deleted. Need to manually create a div here to add
                        //things to
                        $('div.loader_parent').after(dummyrow);
                    } else {
                        topRow.before(dummyrow);
                    }

                    var placeholder = $("div.placeholder:first");
                    var overview_placeholder = $("div.overview:first");

                    // We need this id to plot from URL later
                    overview_placeholder.attr('id', $scope.graphCounter);

                    // insert checkboxes
                    plotdatumcomplete = [];
                    // Select the right container and add in the checkboxes
                    var choiceContainer = $("span.choices#choice-" + $scope.graphCounter);

                    var currPlotSeqInArray = parseInt(choiceContainer.attr('id').split('-')[1]);
                    $scope.plotsinGraph[currPlotSeqInArray] = [];

                    angular.forEach(botReportData, function (value, key) {
                        var choiceDiv = "";
                        if (typeof plots_inc !== 'undefined' && plots_inc.length > 0) {
                            // If this was from a URL, and there were some plot
                            if ( $.inArray(key, plots_inc ) === -1 ) {
                                // If the value does not exist in the plot
                                choiceDiv = $('<div>').addClass('checkbox').append("" +
                                    "<label>" +
                                    "<input name='" + key + "' id = 'id" + key + "' type='checkbox' " +
                                    "value=''>" + key + "</label>"
                                );
                            } else {
                                // Draw normally
                                choiceDiv = $('<div>').addClass('checkbox').append("" +
                                    "<label>" +
                                    "<input name='" + key + "' id = 'id" + key + "' type='checkbox' " +
                                    "checked='checked' value=''>" + key + "</label>"
                                );
                                $scope.plotsinGraph[currPlotSeqInArray].push(key);
                                plotdatumcomplete.push({'data': botReportData[key], 'label': key});
                            }
                        } else {
                            choiceDiv = $('<div>').addClass('checkbox').append("" +
                                "<label>" +
                                "<input name='" + key + "' id = 'id" + key + "' type='checkbox' " +
                                "checked='checked' value=''>" + key + "</label>"
                            );
                            plotdatumcomplete.push({'data': botReportData[key], 'label': key});
                        }
                        choiceContainer.append(choiceDiv);
                    });

                    choiceContainer.find("input").click(plotAccordingToChoices);
                    // We might not want to draw everything here if we got some value on the URL

                    function plotAccordingToChoices() {
                        var currseq = parseInt($(this).parent().parent().parent().attr('id').split('-')[1]);
                        var currPlotSeqInArray = 0;
                        $filter('filter')($scope.plots, function (item) {
                            if (item.seq === currseq) {
                                currPlotSeqInArray = $scope.plots.indexOf(item);
                                return true;
                            }
                            return false;
                        });
                        // Clear existing plot entries
                        $scope.plots[currPlotSeqInArray]['plots'] = [];

                        updatedPlotData = [];
                        choiceContainer.find("input:checked").each(function () {
                            var key = $(this).attr("name");
                            if (key) {
                                updatedPlotData.push(
                                    {
                                        'data': $filter('filter')(plotdatumcomplete, {'label': key})[0]['data'],
                                        'label': key
                                    }
                                );
                                // Update the URL
                                $scope.plots[currPlotSeqInArray]['plots'].push(key);
                            }
                        });
                        console.log("WHTTTTTTTTT");
                        createPlot(updatedPlotData, function () {});
                        $location.path(encodeURIComponent(btoa(JSON.stringify($scope.plots))));
                        $scope.$apply();
                    }

                    $scope.mainplotcomplate = false, $scope.overviewplotcomplete = false;

                    // Hook called after main plot drawn
                    function mainplotdrawn() {
                        $scope.mainplotcomplete = true;
                    }

                    // Hook called after overview plot drawn
                    function overviewplotdrawn() {
                        $scope.overviewplotcomplete = true;
                    }

                    function createPlot(plotdatum, callback) {
                        var mid = 0, end = 0;
                        if (plotdatum.length > 0) {
                            // Will need it for selection on overview chart
                            mid = plotdatum[0]['data'][parseInt(plotdatum[0]['data'].length / 2)][0];
                            end = plotdatum[0]['data'][plotdatum[0]['data'].length - 1][0];
                        }
                        var plot = $.plot(placeholder, plotdatum, {
                            xaxis: {
                                mode: "time",
                                tickLength: 5,
                                timeformat: "%H:%M:%S",
                                min: !start_inc ? mid: +start_inc,
                                max: !end_inc ? end: +end_inc,
                            },
                            crosshair: {
                                mode: "x,y"
                            },
                            yaxis: {
                                axisLabel: testMetrics[0]['name'] + ' (' +
                                (testMetrics[0]['is_better'] === 'up' ? 'up' : 'down') + ' is better)',
                                position: 'left'
                            },
                            grid: {
                                hoverable: true
                            },
                            legend: {
                                show: true,
                                position: "nw"
                            },
                            hooks: {
                                draw: [
                                    mainplotdrawn
                                ]
                            }
                        });

                        var overview = $.plot(overview_placeholder, plotdatum, {
                            series: {
                                lines: {
                                    show: true,
                                    lineWidth: 1
                                },
                                shadowSize: 0
                            },
                            legend: {
                                show: false
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
                                backgroundColor: {colors: ["#ddd", "#fff"]}
                            },
                            rangeselection: {
                                color: "#mar",
                                start: !start_inc ? mid: +start_inc,
                                end: !end_inc ? end: +end_inc,
                                enabled: true,
                                callback: function (o) {
                                    var plotSeq = overview.getPlaceholder().attr('id');
                                    var plotSeqInArray = 0;
                                    $filter('filter')($scope.plots, function (item) {
                                        if (item.seq == plotSeq) {
                                            plotSeqInArray = $scope.plots.indexOf(item);
                                            return true;
                                        }
                                        return false;
                                    });

                                    // Update the URL
                                    $scope.plots[plotSeqInArray]['start'] = o.start;
                                    $scope.plots[plotSeqInArray]['end'] = o.end;

                                    $location.path(encodeURIComponent(btoa(JSON.stringify($scope.plots))));
                                    $scope.$apply();

                                    // updaterangeSelection(o.start, o.end);
                                    var xaxis = plot.getAxes().xaxis;
                                    xaxis.options.min = o.start;
                                    xaxis.options.max = o.end;
                                    plot.setupGrid();
                                    plot.draw();
                                }
                            },
                            hooks: {
                                draw: [
                                    overviewplotdrawn
                                ]
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
                            if (item) {
                                var x = item.datapoint[0], y = item.datapoint[1];
                                var date = new Date(x);
                                var currentPlot = +placeholder.attr('id');
                                hoveredSeriesBot = item.series.label;
                                $("#tooltip").html("<b>" + hoveredSeriesBot + "</b> on <i>" + currentSubtestPath + "</i><br>"
                                    + "<b>Time</b>: " + date.toISOString().split('T')[0] + ", " + date.toISOString().split('T')[1].substring(0, 8) + "<br>"
                                    + "<b>Test Version</b>: " + extraToolTipInfo[currentPlot][hoveredSeriesBot][x]['test_version'].slice(-7) + "<br>"
                                    + "<b>Browser Version</b>: " + extraToolTipInfo[currentPlot][hoveredSeriesBot][x]['browser_version'] + "<br>"
                                    + "<b>Std. Dev</b>: " + parseFloat(extraToolTipInfo[currentPlot][hoveredSeriesBot][x]['stddev']).toFixed(3) + "<br>"
                                    + "<b>Value</b>: " + parseFloat(y).toFixed(3) + " " + testMetrics[0]['unit'] + "<br>"
                                    + "<b>Delta</b> :" + parseFloat(extraToolTipInfo[currentPlot][hoveredSeriesBot][x]['delta']).toFixed(3) + "<br>"
                                    + "<b>Aggregation </b> :" + selectedSubtest.aggregation + "<br>")
                                    .css({top: item.pageY + 5, left: item.pageX + 5})
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

                        $scope.loading = false;
                        $scope.loaded = true;


                        if ($scope.overviewplotcomplete === false || $scope.mainplotcomplete === false) {
                            //We have to wait for this to complete
                            var checkplotdrawn = setInterval(function () {
                                if ($scope.overviewplotcomplete && $scope.mainplotcomplete) {
                                    clearInterval(checkplotdrawn);
                                    callback(true);
                                }
                            }, 500);
                        } else {
                            // Both graphs are plotted, now call the callback
                            callback(true);
                        }
                    }

                    createPlot(plotdatumcomplete, function (plotcompleted) {
                        var plot = {
                            "browser": !selectedBrowser ? 'all' : selectedBrowser.id,
                            "bot": !selectedBot ? 'all' : selectedBot.name,
                            "root_test": selectedTest.root_test.id,
                            "subtest": selectedSubtest.test_path,
                            "seq": $scope.graphCounter,
                            "start": undefined,
                            "end": undefined
                        };
                        if ($scope.plotsinGraph[$scope.graphCounter]) {
                            plot['plots'] = $scope.plotsinGraph[$scope.graphCounter].length > 0 ? $scope.plotsinGraph[$scope.graphCounter] : [];
                        } else {
                            plot['plots'] = [];
                        }
                        $scope.graphCounter = $scope.graphCounter + 1;

                        $scope.plots.push(plot);
                        $location.path(encodeURIComponent(btoa(JSON.stringify($scope.plots))));

                        // Callback might not exist for nature
                        if (callbackondone) {
                            callbackondone($scope.graphCounter);
                        }
                    });
                });
            });
        });
    };
    // Some JQuery stuff - to handle close button clicks
    $(document).on('click','.close_button',function(){
        $(this).parent().parent().parent().remove();
        //TODO: Need to update the URL here as well
    });

    reorderGraphs = function (totalplots) {
        $scope.loading = true;
        var plotsarray = [];

        for (var i=0; i<totalplots; i++) {
            var dummy = $('div#'+ i +'.dummy');
            plotsarray.push({ 'seq': i, data : dummy });
            dummy.detach();
        }

        var plotarraysorted = $filter('orderBy')(plotsarray, '-seq');

        // Redraw the graphs according to sequence
        for (var j=0; j<plotarraysorted.length; j++) {
            $('#plot_area').append(plotarraysorted[j].data);
        }

        $scope.loading = false;
        $scope.loaded = true;
    }

});

