'use strict';

/**
 * @ngdoc filter
 * @name MyBankApp.filter:timeOfDay
 * @function
 * @description
 * # timeOfDay
 * Filter in the MyBankApp.
 */
angular.module('MyBankApp')
  .filter('timeOfDay', function() {
    return function(input, endTime, isEndHr) {
        var military_time = '0000 hrs',
            am_pm = '12 am',
            endHrs= '00 hrs';
        if (!endTime) {
            endTime = 24;
        }
        if (input > endTime || input < 0 || input !== parseInt(input)) {
            return 'Invalid input: ' + input;
        }
        if (isEndHr) {
            endHrs = '59 hrs';
        }
        if (input === endTime) {
            military_time = '2359 hrs';
        } else if (input < 10) {
            military_time = '0' + input + endHrs;
        } else {
            military_time = input + endHrs;
        }
        if (input === 0 || input === 24) {
            am_pm = '12 am';
        } else if (input === 12) {
            am_pm = '12 pm';
        } else if (input > 12) {
            am_pm = (input - 12) + ' pm';
        } else {
            am_pm = input + ' am';
        }
        return am_pm + ' (' + military_time + ')';
    };
  });
