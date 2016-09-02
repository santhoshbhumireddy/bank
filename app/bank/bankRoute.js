'use strict';

angular.module('bank')
.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/account', {
            templateUrl: 'bank/summary.html',
            controller: 'AccountSummaryCtrl',
            label: 'Account Summary'
        })
        .when('/transaction', {
            templateUrl: 'bank/transactions.html',
            controller: 'TransactionCtrl',
            label: 'Transaction Summary'
        })
        .when('/transferfunds', {
            templateUrl: 'bank/payee.html',
            controller: 'TransferFundsCtrl',
            label: 'Registered Payees'
        });
}]);