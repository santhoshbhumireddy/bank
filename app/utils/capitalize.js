'use strict';

/**
 * @ngdoc filter
 * @name MyBankApp.filter:capitalize
 * @function
 * @description
 * # capitalize
 * Filter in the MyBankApp.
 */
angular.module('MyBankApp')
    .filter('capitalize', function() {
        return function(input) {
            if (input && input.length > 0) {
                return input.substring(0, 1).toUpperCase() + input.substring(1);
            }
            return input;
        };
    })
    // TODO: Merge titlecase, capitalise and likewise text formatting filters.
    .filter('beautify', function() {
        return function(input) {
            input = input || '';
            return input.replace(/_/g, ' ').toUpperCase();
        };
    });
