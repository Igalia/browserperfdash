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
    $scope.bots = botFullDetailsForResultsExistFactory.query({
        browser: 'all'
    });
    $scope.platforms = platformFactory.query();
    $scope.gpus = gpuFactory.query();
    $scope.cpus = cpuArchFactory.query();
    $scope.tests = testsForBrowserAndBotFactory.query({
        browser: !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.id,
        bot: !$scope.selectedBot ? null : $scope.selectedBot.name,
    });
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
        $scope.tests = testsForBrowserAndBotFactory.query({
            browser: !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.id,
            bot: !$scope.selectedBot ? null : $scope.selectedBot.name,
        }, function () {
            $scope.bots = botFullDetailsForResultsExistFactory.query({
                browser: !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.id
            });
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
        $scope.selectedDays = !$scope.selectedDays ? 5 : $scope.selectedDays;
        $scope.listLimit = !$scope.listLimit? 10 : $scope.listLimit;
        $scope.selectedBrowserId = !$scope.selectedBrowser ? 'all' : $scope.selectedBrowser.id;
        $scope.selectedPlatformId = !$scope.selectedPlatform ? 'all' : $scope.selectedPlatform.id;
        $scope.selectedCPUId = !$scope.selectedCPU ? 'all' : $scope.selectedCPU.id;
        $scope.selectedGPUId = !$scope.selectedGPU ? 'all' : $scope.selectedGPU.id;
        $scope.selectedTestId = !$scope.selectedTest ? 'all' : $scope.selectedTest.root_test.id;
        $scope.selectedBotName = !$scope.selectedBot ? 'all' : $scope.selectedBot.name;
        $scope.improvement_reports = botReportsImprovementFactory.query({
            days_since: $scope.selectedDays,
            platform: $scope.selectedPlatformId,
            gpu: $scope.selectedGPUId,
            cpu: $scope.selectedCPUId,
            browser: $scope.selectedBrowserId,
            test: $scope.selectedTestId,
            bot: $scope.selectedBotName,
            limit: $scope.listLimit
        }, function (data) {
            if (data.length == 0) {
                $scope.noImprovementsFound = true;
            }
            $scope.loading_improvements = false;
        });
        $scope.regression_reports = botReportsRegressionFactory.query({
            days_since: $scope.selectedDays,
            platform: $scope.selectedPlatformId,
            gpu: $scope.selectedGPUId,
            cpu: $scope.selectedCPUId,
            browser: $scope.selectedBrowserId,
            test: $scope.selectedTestId,
            bot: $scope.selectedBotName,
            limit: $scope.listLimit
        }, function (data) {
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
