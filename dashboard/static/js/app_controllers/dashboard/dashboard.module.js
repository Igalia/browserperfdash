/**
 * Angular controllers for dashboard controls on index.html
 *
 * Created by tthomas@igalia.com on 11/4/17.
 */
app = angular.module(
    'browserperfdash.dashboard.controller',
    [
        'browserperfdash.dashboard.services',
        'ngAnimate',
        'ngSanitize',
        'ui.bootstrap'
    ]
);

app.controller(
    'DeltaController',
    function(
        $scope, botReportsImprovementFactory, botReportsRegressionFactory,
        browserFactory, botFullDetailsForResultsExistFactory, platformFactory,
        gpuFactory, cpuArchFactory, testsForBrowserAndBotFactory, $interval,
        $sce, $filter
    ) {
    $scope.browsers = browserFactory.query();
    $scope.bots = botFullDetailsForResultsExistFactory.query({});
    $scope.platforms = platformFactory.query();
    $scope.gpus = gpuFactory.query();
    $scope.cpus = cpuArchFactory.query();

    $scope.tests_query = angular.extend({}, {
        browser: !$scope.selectedBrowser ? undefined : $scope.selectedBrowser.id,
        bot: !$scope.selectedBot ? undefined : $scope.selectedBot.name,
    });
    $scope.tests = testsForBrowserAndBotFactory.query($scope.tests_query);
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
    $scope.updateOthersOnBrowserChange = function () {
        //There can be chance of test change
        $scope.tests_query_on_browser = angular.extend({}, {
            browser: !$scope.selectedBrowser ? undefined : $scope.selectedBrowser.id,
            bot: !$scope.selectedBot ? undefined : $scope.selectedBot.name,
        });
        $scope.tests = testsForBrowserAndBotFactory.query(
            $scope.tests_query_on_browser, function () {
            $scope.bot_query = angular.extend({}, {
               'browser': !$scope.selectedBrowser ? undefined : $scope.selectedBrowser.id
            });
            $scope.bots = botFullDetailsForResultsExistFactory.query($scope.bot_query);
            $scope.reload();
        });
    };
    $scope.updateOthersOnBotChange = function () {
        if ( !$scope.selectedBot ) {
            $scope.selectedPlatform = '';
            $scope.selectedCPU = '';
            $scope.selectedGPU = '';
        } else {
            $scope.selectedPlatform = $filter('filter')($scope.platforms, {'id': $scope.selectedBot.platform.id})[0];
            $scope.selectedCPU = $filter('filter')($scope.cpus, {'id': $scope.selectedBot.cpuArchitecture.id})[0];
            $scope.selectedGPU = $filter('filter')($scope.gpus, {'id': $scope.selectedBot.gpuType.id})[0];
        }
        $scope.reload();
    };
    $scope.reload = function () {
        $scope.noImprovementsFound = false;
        $scope.noRegressionsFound = false;
        $scope.loading = true;
        $scope.query_params = angular.extend({}, {
            browser: !$scope.selectedBrowser ? undefined : $scope.selectedBrowser.id,
            platform: !$scope.selectedPlatform ? undefined : $scope.selectedPlatform.id,
            gpu: !$scope.selectedGPU ? undefined : $scope.selectedGPU.id,
            cpu: !$scope.selectedCPU ? undefined : $scope.selectedCPU.id,
            test: !$scope.selectedTest ? undefined : $scope.selectedTest.root_test.id,
            bot: !$scope.selectedBot ? undefined : $scope.selectedBot.name,
            days_since: !$scope.selectedDays ? 5 : $scope.selectedDays,
            limit: !$scope.listLimit? 10 : $scope.listLimit
        });

        $scope.improvement_reports = botReportsImprovementFactory.query(
            $scope.query_params, function (data) {
            if (data.length == 0) {
                $scope.noImprovementsFound = true;
            }
            $scope.loading_improvements = false;
        });
        $scope.regression_reports = botReportsRegressionFactory.query(
            $scope.query_params, function (data) {
            if (data.length == 0) {
                $scope.noRegressionsFound = true;
            }
            $scope.loading_regressions = false;
        });
        if (!$scope.loading_improvements && !$scope.loading_regressions) {
            $scope.loading = false;
        }
    };
    $scope.updateBotPopover = function (botname) {
        currentbot = $filter('filter')($scope.bots, {'name': botname})[0];
        $scope.bot_cpu_arch = currentbot.cpuArchitecture.name;
        $scope.bot_gpu_type = currentbot.gpuType.name;
        $scope.bot_platform = currentbot.platform.name;
        $scope.loadedBotData = true;
    };
    $scope.reload();
});
