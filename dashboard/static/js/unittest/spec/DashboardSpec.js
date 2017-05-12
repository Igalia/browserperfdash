// Provide real fabricated data to test on - the application loads it from /static/js/unittestsdummy/ and verify
var browsers = [{"id":"chrome","name":"Chrome Browser"}, {"id":"epiphany","name":"Epiphany (GNOME Web)"},
    {"id":"firefox","name":"Firefox"}];
var bots = [{"name":"buildbox3","platform":{"id":1,"name":"Linux/X11"},"cpuArchitecture":{"id":1,"name":"amd64"},
    "gpuType":{"id":3,"name":"mesa-llvmpipe"}},{"name":"getafix","platform":{"id":1,"name":"Linux/X11"},
    "cpuArchitecture":{"id":2,"name":"armv7"},"gpuType":{"id":3,"name":"mesa-llvmpipe"}}];
var platforms = [{"id":1,"name":"Linux/X11"}];
var gpus = [{"id":3,"name":"mesa-llvmpipe"}];
var cpus = [{"id":1,"name":"amd64"},{"id":2,"name":"armv7"}];
var tests = [{"root_test":{"id":"dromaeo-cssquery"}},{"root_test":{"id":"dromaeo-dom"}},
    {"root_test":{"id":"dromaeo-jslib"}},{"root_test":{"id":"es6bench"}},
    {"root_test":{"id":"jetstream"}},{"root_test":{"id":"jsbench"}},
    {"root_test":{"id":"kraken"}},{"root_test":{"id":"motionmark"}},
    {"root_test":{"id":"octane"}},{"root_test":{"id":"sunspider"}}];

describe('DeltaController', function() {
    beforeEach(module('browserperfdash.dashboard.static'));
    var $controller, resource, $filter;

    beforeEach(inject(function(_$controller_, _$filter_, $rootScope, $q){
        // The injector unwraps the underscores (_) from around the parameter names when matching
        var $injector = angular.injector(['ng', 'ngResource']);
        var $resource = $injector.get('$resource');

        $controller = _$controller_;
        $filter = _$filter_;

        $scope = $rootScope.$new();

        it("intercept browserFactory", inject(function(browserFactory) {
            spyOn(browserFactory, 'query').and.returnValue(
                $resource('/static/js/unittest/dummy/browsers.json').query()
            );
        }));
        it("intercept browserFactory", inject(function(botFullDetailsForResultsExistFactory) {
            spyOn(botFullDetailsForResultsExistFactory, 'query').and.returnValue(
                $resource('/static/js/unittest/dummy/bots.json').query()
            );
        }));
        it("intercept platformFactory", inject(function(platformFactory) {
            spyOn(platformFactory, 'query').and.returnValue(
                $resource('/static/js/unittest/dummy/platforms.json').query()
            );
        }));
        it("intercept gpuFactory", inject(function(gpuFactory) {
            spyOn(gpuFactory, 'query').and.returnValue(
                $resource('/static/js/unittest/dummy/gpus.json').query()
            );
        }));
        it("intercept cpuArchFactory", inject(function(cpuArchFactory) {
            spyOn(cpuArchFactory, 'query').and.returnValue(
                $resource('/static/js/unittest/dummy/cpus.json').query()
            );
        }));
        it("intercept testsForBrowserAndBotFactory", inject(function(testsForBrowserAndBotFactory) {
            spyOn(testsForBrowserAndBotFactory, 'query').and.returnValue(
                $resource('/static/js/unittest/dummy/tests.json').query()
            );
        }));

        $controller('DeltaController', { $scope: $scope });
    }));

    describe('Populating all the select boxes via service query', function () {
        it("check if all select boxes are populated correctly", function (done) {
            //Load all elements correctly
            $scope.browsers.$promise.then(function () {
                expect($scope.browsers.length).toEqual(browsers.length);
                $scope.bots.$promise.then(function () {
                    expect($scope.bots.length).toEqual(bots.length);
                    $scope.platforms.$promise.then(function () {
                        expect($scope.platforms.length).toEqual(platforms.length);
                        $scope.gpus.$promise.then(function () {
                            expect($scope.gpus.length).toEqual(gpus.length);
                            $scope.cpus.$promise.then(function () {
                                expect($scope.cpus.length).toEqual(cpus.length);
                                $scope.tests.$promise.then(function () {
                                    expect($scope.tests.length).toEqual(tests.length);
                                    done();
                                });
                            });
                        });
                    });
                });
            });
        });

        it("check if paltform, gpu and cpu changed correctly on bot change", function (done) {
            $scope.bots.$promise.then(function() {
                $scope.platforms.$promise.then(function () {
                    $scope.cpus.$promise.then(function() {
                        $scope.gpus.$promise.then(function () {
                            // At this point, expect platform, cpu and GPU to point to "All objects"
                            expect($scope.selectedGPU).toBeUndefined();
                            expect($scope.selectedBot).toBeUndefined();
                            expect($scope.selectedPlatform).toBeUndefined();
                            // Now change the bot to check if the change is reflected on the other selects
                            // {"name":"buildbox3","platform":{"id":1,"name":"Linux/X11"},"cpuArchitecture":{"id":1,"name":"amd64"},
                            // "gpuType":{"id":3,"name":"mesa-llvmpipe"}}
                            $scope.selectedBot = $filter('filter')($scope.bots, {'name': "buildbox3" })[0];
                            // Manually fire the select box change
                            // We should expect calls to botReportsImprovementFactory
                            it("intercept botReportsImprovementFactory",
                                inject(function(botReportsImprovementFactory, botReportsRegressionFactory) {
                                    // Create spies to watch calls to APIs
                                    spyOn(botReportsImprovementFactory, 'query');
                                    spyOn(botReportsRegressionFactory, 'query');
                                    botReportsImprovementFactory.query.and.callFake(function(arguments) {
                                        // The following part gets called only after the $scope.updateOthersOnBotChange()
                                        expect(arguments.platform).toEqual($scope.selectedBot.platform.id);
                                        expect(arguments.gpu).toEqual($scope.selectedBot.gpuType.id);
                                        expect(arguments.cpu).toEqual($scope.selectedBot.cpuArchitecture.id);
                                    });
                                    botReportsRegressionFactory.query.and.callFake(function(arguments) {
                                        // The following part gets called only after the $scope.updateOthersOnBotChange()
                                        expect(arguments.platform).toEqual($scope.selectedBot.platform.id);
                                        expect(arguments.gpu).toEqual($scope.selectedBot.gpuType.id);
                                        expect(arguments.cpu).toEqual($scope.selectedBot.cpuArchitecture.id);
                                    });
                                    // Should trigger the above spies
                                    $scope.updateOthersOnBotChange();
                                    // Check if the select combos changed correctly
                                    expect($scope.selectedGPU).toBe(
                                        $filter('filter')($scope.gpus, {'id': $scope.selectedBot.gpuType.id })[0]
                                    );
                                    expect($scope.selectedCPU).toBe(
                                        $filter('filter')($scope.cpus, {'id': $scope.selectedBot.cpuArchitecture.id })[0]
                                    );
                                    expect($scope.selectedPlatform).toBe(
                                        $filter('filter')($scope.platforms, {'id': $scope.selectedBot.platform.id })[0]
                                    );

                                    // We should expect calls to get improvements and regressions
                                    expect(botReportsImprovementFactory.query).toHaveBeenCalled();
                                    expect(botReportsRegressionFactory.query).toHaveBeenCalled();
                                }));
                            done();
                        });
                    });
                });
            });
        });
    });
});