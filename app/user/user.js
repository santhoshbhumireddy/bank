/*global angular, window*/

/**
 * @ngdoc function
 * @name MyBankApp.controller:LoginCtrl
 * @description
 * # LoginCtrl
 * Controller of the MyBankApp
 */
angular
    .module('user')
    .controller('LoginCtrl', ['$rootScope', '$scope', 'LoginService', 'localStorageService', 'toaster', '$location',
        function ($rootScope, $scope, LoginService, localStorageService, toaster, $location) {
            'use strict';
            $scope.validate = function () {
                $scope.validateFormFlag = true;
                $scope.logInForm.submitted=true;
                if ($scope.logInForm.$valid) {
                    return true;
                } else {
                    toaster.pop('error', 'Error', 'Enter valid user name and password');
                    return false;
                }
                if($scope.validateFormFlag){
                    toaster.pop('error', 'Error', 'Enter valid user name and password');
                    return false;
                }
                $scope.validateFormFlag = false;
                return true;
            };
            $scope.logIn = function () {
                if (!$scope.validate()) {
                    return false;
                }
                var payload = {
                    'auth': {
                        'user_name': $scope.userName,
                        'password': $scope.password
                    }
                };
                LoginService.auth(payload).then(function (result) {
                    if (result) {
                        var userInfo = result.data.response.user_info;
                        localStorageService.set('userInfo', userInfo);
                        $rootScope.loggedIn = true;
                        $rootScope.modalInstance.dismiss('cancel');
                        $location.path('/account');
                        return;
                    } else {
                        $scope.dirty = false;
                    }
                });
            };
        }
        ])
    .controller('SignUpCtrl', ['$rootScope', '$scope', 'LoginService', 'localStorageService', 'toaster', '$location', '$route',
        function ($rootScope, $scope, LoginService, localStorageService, toaster, $location, $route) {
            'use strict';
            $scope.userInfo = {};
            $scope.validate = function () {
                $scope.validateFormFlag = true;
                $scope.signUpForm.submitted=true;
                if ($scope.signUpForm.$valid) {
                    return true;
                } else {
                    return false;
                }
                if($scope.validateFormFlag){
                    toaster.pop('error', 'Error', 'Invalid details');
                    return false;
                }
                $scope.validateFormFlag = false;
                return true;
            };
            $scope.signUp = function () {
                if (!$scope.validate()) {
                    return false;
                }
                var payload = {
                    'user_info': $scope.userInfo
                };
                LoginService.register(payload).then(function (result) {
                    if (result) {
                        var accountId = result.data.response.user_info.account_id;
//                          $location.path('/');
                        $rootScope.modalInstance.dismiss('cancel');
                        $route.reload();
                        toaster.pop('success', 'Account', 'Created Succesfully Your Account ID:' + accountId);
                        return;
                    } else {
                        $scope.dirty = false;
                    }
                });
            };
        }
        ]);

angular.module('utils')
    .service('LoginService', ['InvokeHTTP',
        function (InvokeHTTP) {
            'use strict';
            return {
                auth: function (payload) {
                    return InvokeHTTP.create('/auth', payload).then(function (result) {
                        return result;
                    });
                },
                register: function (payload) {
                    return InvokeHTTP.create('/register', payload).then(function (result) {
                        return result;
                    });
                }
            }
        }]);
