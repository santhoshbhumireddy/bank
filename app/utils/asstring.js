/*global angular*/

/**
 * @ngdoc filter
 * @name MyBankApp.filter:asString
 * @function
 * @description
 * # asString
 * Filter in the MyBankApp.
 */
angular.module('MyBankApp')
    .filter('asString', function() {
        'use strict';
        return function(input) {
            if (!input) {
                input = [];
            }
            return input.join(', ');
        };
    });
