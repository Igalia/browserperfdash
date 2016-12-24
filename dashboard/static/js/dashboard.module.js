app = angular.module('browserperfdash.dashboard.static', ['ngResource']);

app .factory('botReportsFactory', function($resource) {
  return $resource('/dash/results');
});

app.controller('AppController', function($scope, $http, botReportsFactory, $interval) {
    $scope.reload = function () {
        $scope.reports = botReportsFactory.query();
    };
    $scope.reload();
    $interval($scope.reload, 50000);
});