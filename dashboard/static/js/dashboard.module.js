app = angular.module('browserperfdash.dashboard.static', []);

app.controller('AppController', function($scope, $http) {
    $scope.reports = [];
    $http.get('/dash/results')
        .then(function(result) {
            angular.forEach(result.data, function (report) {
                $scope.reports.push(report);
            })
        });
});