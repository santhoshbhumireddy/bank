'use strict';

/**
 * @ngdoc filter
 * @name MyBankApp.filter:title_case
 * @function
 * @description
 * # title_case
 * Filter in the MyBankApp.
 */
angular.module('MyBankApp')
  .filter('title_case', function() {
    return function(input) {
      input = input || '';
      return input.replace(/\w\S*/g, function(txt) {return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
    };
  });
