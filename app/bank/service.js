/*global angular, document */
/**
 * @ngdoc service
 * @name MyBankApp.query
 * @description
 * # query
 * Service in the MyBankApp.
 */
angular.module('MyBankApp')
    .service('Account', ['InvokeHTTP', function (InvokeHTTP) {
        'use strict';
        return {
            list: function (query_params) {
                return InvokeHTTP.fetch('/accounts', {params:query_params}).then(function (result) {
                    return result.data.response;
                });
            },
            fetch: function (accountId) {
                return InvokeHTTP.fetch('/account/' + accountId).then(function (result) {
                    return result.data.response;
                });
            },
            create: function (payload) {
                return InvokeHTTP.create('/accounts', payload).then(function (result) {
                    return result.data.response;
                });
            },
            update: function (accountId, payload) {
                return InvokeHTTP.edit('/account/' + accountId, payload).then(function (result) {
                    return result.data.response;
                });
            },
            delete: function (accountId) {
                return InvokeHTTP.delete('/account/' + accountId).then(function (result) {
                    return result.data.response;
                });
            }
        };
    }])
    .service('Payee', ['InvokeHTTP', function (InvokeHTTP) {
        'use strict';
        return {
            list: function (query_params) {
                return InvokeHTTP.fetch('/payees', {params:query_params}).then(function (result) {
                    return result.data.response;
                });
            },
            fetch: function (payeeId) {
                return InvokeHTTP.fetch('/payee/' + payeeId).then(function (result) {
                    return result.data.response;
                });
            },
            create: function (payload) {
                return InvokeHTTP.create('/payees', payload).then(function (result) {
                    return result.data.response;
                });
            },
            update: function (payeeId, payload) {
                return InvokeHTTP.edit('/payee/' + payeeId, payload).then(function (result) {
                    return result.data.response;
                });
            },
            delete: function (payeeId) {
                return InvokeHTTP.delete('/payee/' + payeeId).then(function (result) {
                    return result.data.response;
                });
            }
        };
    }])
    .service('Transaction', ['InvokeHTTP', function (InvokeHTTP) {
        'use strict';
        return {
            list: function (query_params) {
                return InvokeHTTP.fetch('/transactions', {params:query_params}).then(function (result) {
                    return result.data.response;
                });
            },
            fetch: function (transactionId) {
                return InvokeHTTP.fetch('/transaction/' + transactionId).then(function (result) {
                    return result.data.response;
                });
            },
            create: function (payload) {
                return InvokeHTTP.create('/transactions', payload).then(function (result) {
                    return result.data.response;
                });
            },
            update: function (transactionId, payload) {
                return InvokeHTTP.edit('/transaction/' + transactionId, payload).then(function (result) {
                    return result.data.response;
                });
            },
            delete: function (transactionId) {
                return InvokeHTTP.delete('/transaction/' + transactionId).then(function (result) {
                    return result.data.response;
                });
            }
        };
    }]);