'use strict';

/**
 * @ngdoc directive
 * @name MyBankApp.directive:footer
 * @description
 * # footer
 */
angular.module('MyBankApp')
  .directive('footer', function() {
    return {
      restrict: 'A',
      templateUrl: 'utils/footer.html'
    };
  });
