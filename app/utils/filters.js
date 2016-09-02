'use strict';

angular.module('utils')
  .filter('translateID', function() {
    return function(input, mapping) {
        return mapping[input] || input;
    };
  });
