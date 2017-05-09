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
    var $controller, $filter;

    beforeEach(inject(function(_$controller_, _$filter_, $injector, $rootScope, $q){
        // The injector unwraps the underscores (_) from around the parameter names when matching
        var $injector = angular.injector(['ng', 'ngResource']);
        var $resource = $injector.get('$resource');

        $scope = $rootScope.$new();
        $filter = _$filter_;

        $controller = _$controller_;
        it("intercept browserFactory", inject(function(browserFactory, $rootScope) {
            spyOn(browserFactory, 'query').and.returnValue(
                $resource('/static/js/unittestdummy/browsers.json').query()
            );
        }));
        it("intercept browserFactory", inject(function(botFullDetailsForResultsExistFactory) {
            spyOn(botFullDetailsForResultsExistFactory, 'query').and.returnValue(
                $resource('/static/js/unittestdummy/bots.json').query()
            );
        }));
        it("intercept platformFactory", inject(function(platformFactory) {
            spyOn(platformFactory, 'query').and.returnValue(
                $resource('/static/js/unittestdummy/platforms.json').query()
            );
        }));
        it("intercept gpuFactory", inject(function(gpuFactory) {
            spyOn(gpuFactory, 'query').and.returnValue(
                $resource('/static/js/unittestdummy/gpus.json').query()
            );
        }));
        it("intercept cpuArchFactory", inject(function(cpuArchFactory) {
            spyOn(cpuArchFactory, 'query').and.returnValue(
                $resource('/static/js/unittestdummy/cpus.json').query()
            );
        }));
        it("intercept testsForBrowserAndBotFactory", inject(function(testsForBrowserAndBotFactory) {
            spyOn(testsForBrowserAndBotFactory, 'query').and.returnValue(
                $resource('/static/js/unittestdummy/tests.json').query()
            );
        }));
        $controller('DeltaController', { $scope: $scope });
    }));

    describe('Populating the combo boxes correctly', function () {
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
    })
});
