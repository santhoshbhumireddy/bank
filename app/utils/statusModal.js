/*global angular*/

/**
 * @ngdoc function
 * @name MyBankApp.controller:DeleteStatusCtrl
 * @description
 * # StatusModalCtrl
 * Controller of the MyBankApp
 */
angular.module('MyBankApp')
    .controller('StatusModalCtrl', ['$scope', '$modalInstance', 'InvokeHTTP', 'Info',
        function($scope, $modalInstance, InvokeHTTP, Info) {
            'use strict';
            $scope.info = Info;
            $scope.deleteStatus = function(status) {
                $scope.status = status;
                $modalInstance.close($scope.status);
            };

            $scope.cancel = function() {
                $modalInstance.dismiss('cancel');
            };

            $scope.close = function() {
                $modalInstance.close();
            };

            //TODO : Move to algo.js, Anshu Choubey
            $scope.downloadResource = function(url) {
                $modalInstance.close();
                InvokeHTTP.fetch('/grantAccess/' + url).then(function(result) {
                    var name = result.data.response.name, url = result.data.response.url,
                        dwnld = document.createElement('a');
                    dwnld.setAttribute('href', url);
                    dwnld.setAttribute('target', '_blank');
                    dwnld.setAttribute('download', name);
                    document.body.appendChild(dwnld);
                    dwnld.click();
                    document.body.removeChild(dwnld);
                });
            };
        }]);
