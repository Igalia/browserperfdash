app = angular.module('browserperfdash.dashboard.static', ['ngResource']);

app .factory('botReportsFactory', function($resource) {
  return $resource('/dash/results');
});

app.controller('AppController', function($scope, $http, botReportsFactory) {
    $scope.reports = botReportsFactory.query();
    // $http.get('/dash/results')
    //     .then(function(result) {
    //         angular.forEach(result.data, function (report) {
    //             $scope.reports.push(report);
    //         })
    //     });
});