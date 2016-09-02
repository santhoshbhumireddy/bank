/*global document, window*/

/**
 * @ngdoc overview
 * @name MyBankApp
 * @description
 * # MyBankApp
 *
 * Main module of the application.
 */

angular.module('utils', [
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'toaster',
    'ui.bootstrap'
]);

angular.module('user', [
    'ngCookies',
    'ngRoute',
    'utils',
    'toaster',
    'ui.bootstrap',
    'LocalStorageModule'
]);

angular.module('bank', [
    'datatables',
    'ngCookies',
    'ngRoute',
    'utils',
    'toaster',
    'ui.bootstrap',
    'LocalStorageModule'
]);
angular
    .module('MyBankApp', [
        'checklist-model',
        'ng-breadcrumbs',
        'ngAnimate',
        'ngCookies',
        'ngMessages',
        'ngResource',
        'ngRoute',
        'ngSanitize',
        'toaster',
        'ui.bootstrap',
        'ui.select',
        'ui.utils',
        'bank',
        'user',
        'utils',
        'LocalStorageModule'
    ])
    .config(function ($routeProvider) {
        'use strict'
        $routeProvider
            .when('/', {
                templateUrl: 'main/main.html',
//                controller: 'MainCtrl',
            })
            .otherwise({
                redirectTo: '/'
            });
    })
    .run(function ($cookieStore, $rootScope, $location, $modal, localStorageService, toaster) {
        'use strict';
        var baseUrl = window.location.protocol + '//' + window.location.host;
        $rootScope.redirectUrl = '/';
        $rootScope.isSelected = {'account': 'selected'};
        $rootScope.isLoginPage = function () {
            if (!$rootScope.loggedIn) {
                return true;
            }
        };
        $rootScope.openModal = function (template, controller, info, size) {
            this.modalInstance = $modal.open({
                templateUrl: template,
                controller: controller,
                size: size,
                // backdrop: 'static',
                resolve: {
                    Info: function () {
                        return {'info': info};
                    }
                }
            });
        };
        $rootScope.signup = function (report) {
            var info = {};
            $rootScope.openModal('user/signup.html', 'SignUpCtrl', info, 'md');
        };
        $rootScope.login = function (report) {
            var info = {};
            $rootScope.openModal('user/login.html', 'LoginCtrl', info, 'md');
        };
        $rootScope.signout = function () {
            $cookieStore.remove('USER_SSID');
            $rootScope.loggedIn = false;
            window.location.replace( baseUrl + '/');
        };
        $rootScope.$on('$locationChangeStart', function (event, next) {
            //  delete window.ATL_JQ_PAGE_PROPS;
            var location = next.split('#')[1];
            if (document.cookie.indexOf('USER_SSID') === -1) {
                //  event.preventDefault();
                $rootScope.loggedIn = false;
                if (location && location !== '/') {
                    window.location.replace(baseUrl+ '/');
                }
            } else {
                $rootScope.loggedIn = true;
            }
            var items = ['account', 'transaction', 'transferfunds'];
            $rootScope.isSelected = {};
            angular.forEach(items, function (item) {
                if ($location.path().indexOf(item) !== -1) {
                    $rootScope.isSelected[item] = 'selected';
                }
            });
        });
    });