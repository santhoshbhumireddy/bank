/*global angular*/

/**
 * @ngdoc service
 * @name MyBankApp.InvokeHTTP
 * @description
 * # InvokeHTTP
 * Service in the MyBankApp.
 */
angular.module('utils')
    .service('InvokeHTTP', ['$http', 'Utils',
        function ($http, Utils) {
            'use strict';
            this.invoke = function (func, url, payload, headers) {
                return func(url, payload, headers).then(function (result) {
                    return Utils.check_response(result);
                }, function (result) {
                    return Utils.check_response(result);
                });
            };
            this.fetch = function (url, query_params) {
                return this.invoke($http.get, url, query_params);
            };
            this.cachedFetch = function (url) {
                return this.invoke($http.get, url, {cache: true});
            };
            this.create = function (url, payload) {
                return this.invoke($http.post, url, payload);
            };
            this.edit = function (url, payload) {
                return this.invoke($http.put, url, payload);
            };
            this.delete = function (url) {
                return this.invoke($http.delete, url);
            };
            this.upload = function (path, data, headers) {
                return this.invoke($http.post, path, data, headers);
            };
        }]);
