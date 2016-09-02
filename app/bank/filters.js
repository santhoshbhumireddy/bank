/*global angular */
/**
 * @ngdoc filter
 * @name MyBankApp.filter:sort
 * @function
 * @description
 * # sort
 * Filter in the iqt application.
 */
angular.module('MyBankApp')
    .filter('sort', function () {
        'use strict';
        return function (input) {
            if (input !== undefined) {
                return input.sort();
            }
        };
    })
    .filter('removeOptions', function () {
        'use strict';
        return function (input) {
            if (input !== undefined) {
                var filtered = angular.copy(input),
                    options = ['Advertiser ID', 'Date'];
                angular.forEach(options, function (option) {
                    var optionIndex = filtered.indexOf(option);
                    if (optionIndex !== -1) {
                        filtered.splice(optionIndex, 1);
                    }
                });
                return filtered;
            }
        };
    })
    .filter('getFilterString', function () {
        'use strict';
        return function (query) {
            if (query !== undefined) {
                var re = /.*WHERE\s+(.*)\s+GROUP BY.*/, filterString = query.replace(re, '$1');
                if (filterString !== query) {
                    return filterString;
                }
                return '';
            }
        };
    })
    .filter('getHavingString', function () {
        'use strict';
        return function (query) {
            if (query !== undefined) {
                var temp = query.split('HAVING');
                if (temp.length === 2) {
                    return temp[1].trim();
                }
                return '';
            }
        };
    })
    .filter('range', function() {
        'use strict';
        // It generates numbers up to max, not including max starting from min
        return function(input, min, max) {
           if (max === undefined) {
                max = min;
                min = 0;
            }
           for (var i = min; i < max; i++) {
                input.push(i);
            }
            return input;
        };
    });

