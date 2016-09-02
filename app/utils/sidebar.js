/*global jQuery*/
'use strict';

/**
 * @ngdoc directive
 * @name MyBankApp.directive:sidebar
 * @description
 * # sidebar
 */
angular.module('MyBankApp')
    .directive('sidebar', function() {
        return {
            restrict: 'A',
            templateUrl: 'utils/sidebar.html',
            link: function(scope, element) {
                jQuery('#jiraCollector').unbind('click');
                window.ATL_JQ_PAGE_PROPS = {
                    'triggerFunction': function(showCollectorDialog) {
                        //Requires that jQuery is available!
                        element.find('#jiraCollector').click(function(e) {
                            e.preventDefault();
                            showCollectorDialog();
                        });
                    }
                };
            }
        };
    });
