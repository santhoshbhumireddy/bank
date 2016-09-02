'use strict';

/**
 * @ngdoc filter
 * @name MyBankApp.filter:yesno
 * @function
 * @description
 * # short description
 * Filter in the MyBankApp.
 */
angular.module('MyBankApp')
    .filter('shortDescription', function() {
        return function(input, length) {
            if (!length) {
                length = 20;
            }
            input = input || '';
            if (input.length > length) {
                return input.slice(0, length) + '...';
            } else {
                return input;
            }
        };
    });
