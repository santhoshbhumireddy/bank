'use strict';

angular.module('user')
.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/login', {
            templateUrl: 'user/login.html',
            controller: 'LoginCtrl',
        })
        .when('/signup', {
            templateUrl: 'user/signup.html',
            controller: 'SignUpCtrl',
        })
}]);
