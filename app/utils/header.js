'use strict';

/**
 * @ngdoc directive
 * @name MyBankApp.directive:header
 * @description
 * # header
 */
angular.module('MyBankApp')
  .directive('header', function(localStorageService) {
    return {
      restrict: 'A',
      templateUrl: 'utils/header.html',
        link: function($scope) {
            $scope.getUserName = function() {
                if (localStorageService.get('userInfo') !== null) {
                    return localStorageService.get('userInfo').user_name;
                }
                return null;
            };
        }
    };
  });
