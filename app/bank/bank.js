/*global angular, $ */
/**
 * MyBankApp Controllers
 */

angular.module('MyBankApp')
    .controller('AccountSummaryCtrl', ['$scope', 'Account', 'localStorageService', 'DTOptionsBuilder', 'DTColumnDefBuilder', '$modal', '$filter', '$route', '$interval', '$location', 'breadcrumbs', 'toaster',
        function ($scope, Account, localStorageService, DTOptionsBuilder, DTColumnDefBuilder, $modal, $filter, $route, $interval, $location, breadcrumbs, toaster) {
            'use strict';
            $scope.dtOptions = DTOptionsBuilder.newOptions().withPaginationType('full_numbers');
            $scope.dtColumnDefs = [
                DTColumnDefBuilder.newColumnDef(0),
                //DTColumnDefBuilder.newColumnDef(1).notVisible(),
                //DTColumnDefBuilder.newColumnDef(2).notSortable()
            ];
            $scope.breadcrumbs = breadcrumbs;
            $scope.showLoading = true;
            $scope.user = localStorageService.get('userInfo');
            $scope.dt = new Date();
            $scope.fetch_account = function () {
                var accountID = $scope.user.account_id;
                Account.fetch(accountID).then(function (result) {
                    if (result) {
                        $scope.account = result.account;
                    }
                    $scope.showLoading = false;
                });
            };
            $scope.fetch_account();
            $scope.openModal = function (templateUrl, controller, info, size) {
                $scope.modalInstance = $modal.open({
                    templateUrl: templateUrl,
                    controller: controller,
                    size: size,
//                    backdrop: 'static',
                    resolve: {
                        Info: function () {
                            return info;
                        }
                    }
                });
            };
            $scope.deposit = function () {
                var info = {
                    'transaction_type': 'Deposit'
                }
                $scope.openModal('bank/transaction.html', 'makeTransactionCtrl', info, 'md');
            };
            $scope.withdraw = function () {
                var info = {
                    'transaction_type': 'Withdraw'
                }
                $scope.openModal('bank/transaction.html', 'makeTransactionCtrl', info, 'md');
            };
        }]
        );
angular.module('MyBankApp')
    .controller('TransactionCtrl', ['$scope', 'Transaction', 'localStorageService', 'DTOptionsBuilder', 'DTColumnDefBuilder', '$modal', '$filter', '$route', '$interval', '$location', 'breadcrumbs', 'toaster',
        function ($scope, Transaction, localStorageService, DTOptionsBuilder, DTColumnDefBuilder, $modal, $filter, $route, $interval, $location, breadcrumbs, toaster) {
            'use strict';
            $scope.dtOptions = DTOptionsBuilder.newOptions().withPaginationType('full_numbers');
            $scope.dtColumnDefs = [
                DTColumnDefBuilder.newColumnDef(0),
                //DTColumnDefBuilder.newColumnDef(1).notVisible(),
                //DTColumnDefBuilder.newColumnDef(2).notSortable()
            ];
            $scope.breadcrumbs = breadcrumbs;
            $scope.showLoading = true;
            $scope.transactions = [];
            $scope.user = localStorageService.get('userInfo');
            $scope.fetch_all = function () {
                var queryParams = {'account_id':$scope.user.account_id}
                Transaction.list({'query_params':queryParams}).then(function (result) {
                    if (result) {
                        $scope.transactions = result.transactions;
                    }
                    $scope.showLoading = false;
                });
            };
            $scope.fetch_all()
        }]
        );
angular.module('MyBankApp')
    .controller('TransferFundsCtrl', ['$scope', 'Payee', 'localStorageService', 'DTOptionsBuilder', 'DTColumnDefBuilder', '$modal', '$filter', '$route', '$interval', '$location', 'breadcrumbs', 'toaster',
        function ($scope, Payee, localStorageService, DTOptionsBuilder, DTColumnDefBuilder, $modal, $filter, $route, $interval, $location, breadcrumbs, toaster) {
            'use strict';
            $scope.dtOptions = DTOptionsBuilder.newOptions().withPaginationType('full_numbers');
            $scope.dtColumnDefs = [
                DTColumnDefBuilder.newColumnDef(0),
                //DTColumnDefBuilder.newColumnDef(1).notVisible(),
                //DTColumnDefBuilder.newColumnDef(2).notSortable()
            ];
            $scope.breadcrumbs = breadcrumbs;
            $scope.showLoading = true;
            $scope.payees = [];
            $scope.user = localStorageService.get('userInfo');
            $scope.fetch_all = function () {
                var queryParams = {'user_id':$scope.user.id}
                Payee.list({'query_params':queryParams}).then(function (result) {
                    if (result) {
                        $scope.payees = result.payees;
                    }
                    $scope.showLoading = false;
                });
            };
            $scope.fetch_all()
            $scope.openModal = function (templateUrl, controller, info, size) {
                $scope.modalInstance = $modal.open({
                    templateUrl: templateUrl,
                    controller: controller,
                    size: size,
//                    backdrop: 'static',
                    resolve: {
                        Info: function () {
                            return info;
                        }
                    }
                });
            };
            $scope.addPayee = function () {
                var info = {}
                $scope.openModal('bank/addPayee.html', 'addPayeeCtrl', info, 'md');
            };
            $scope.makePayment = function (payee) {
                var info = {
                    'transaction_type': 'ThirdParty',
                    'dst_account_id': payee.account_id
                }
                $scope.openModal('bank/transaction.html', 'makeTransactionCtrl', info, 'md');
            };
            $scope.deletePayee = function (payee) {
                var info = {
                    heading: null,
                    alert: true,
                    message: null
                };
                info.message = '<p>Do you want to delete payee <b>' + payee.nick_name + '</b>?</p>';
                $scope.openModal('utils/statusModal.html', 'StatusModalCtrl', info, 'sm');
                $scope.modalInstance.result.then(function (status) {
                    if (status) {
                        Payee.delete(payee.id).then(function (result) {
                            if (result) {
                                var index = $scope.payees.indexOf(payee);
                                $scope.payees.splice(index, 1);
                            }
                            toaster.pop('success', 'Payee', 'Deleted successfully');
                        });
                    }
                });
            }
        }]
        );
angular.module('MyBankApp')
    .controller('addPayeeCtrl', ['$scope', '$route', '$modalInstance', '$location', 'Payee', 'toaster', 'Info',
        function($scope, $route, $modalInstance, $location, Payee, toaster, Info) {
            'use strict';
            $scope.payeeInfo = {};
            $scope.transactionTypes = ['INTERNAL', 'NEFT', 'IMPS'];
            $scope.payeeInfo.type = $scope.transactionTypes[0];
            $scope.validate = function () {
                $scope.validateFormFlag = true;
                $scope.addPayeeForm.submitted=true;
                if ($scope.addPayeeForm.$valid) {
                    return true;
                } else {
                    toaster.pop('error', 'Error', 'Invalid details');
                    return false;
                }
                if($scope.validateFormFlag){
                    toaster.pop('error', 'Error', 'Invalid details');
                    return false;
                }
                $scope.validateFormFlag = false;
                return true;
            };
            $scope.add = function () {
               if (!$scope.validate()) {
                    return false;
               }
               var payload = {
                    'payee_info': $scope.payeeInfo
               };
               Payee.create(payload).then(function (result) {
                    $modalInstance.dismiss('cancel');
                    toaster.pop('success', 'Payee', 'Added successfully');
                    $route.reload();
                    return;
               });
            };
            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };
        }
    ]);
angular.module('MyBankApp')
    .controller('makeTransactionCtrl', ['$scope', '$route', '$modalInstance', '$location', 'Transaction', 'localStorageService', 'toaster', 'Info',
        function($scope, $route, $modalInstance, $location, Transaction, localStorageService, toaster, Info) {
            'use strict';
            $scope.user = localStorageService.get('userInfo');
            $scope.transactionType = Info.transaction_type;
            $scope.dstAccountID = Info.dst_account_id;
            $scope.srcAccountID = $scope.user.account_id;
            $scope.transactionInfo = {};
            $scope.validate = function () {
                $scope.validateFormFlag = true;
                $scope.transactionForm.submitted=true;
                if ($scope.transactionForm.$valid) {
                    return true;
                } else {
                    toaster.pop('error', 'Error', 'Invalid details');
                    return false;
                }
                if($scope.validateFormFlag){
                    toaster.pop('error', 'Error', 'Invalid details');
                    return false;
                }
                $scope.validateFormFlag = false;
                return true;
            };
            $scope.makeTransaction = function () {
               if (!$scope.validate()) {
                    return false;
               }
               $scope.transactionInfo.src_account_id = $scope.srcAccountID;
               $scope.transactionInfo.dst_account_id = $scope.dstAccountID;
               $scope.transactionInfo.transaction_type = $scope.transactionType;
               console.log($scope.transactionInfo);
               var payload = {
                    'transaction_info': $scope.transactionInfo
               };
               Transaction.create(payload).then(function (result) {
                    $modalInstance.dismiss('cancel');
                    toaster.pop('success', 'Transaction', 'Made successfully');
                    $route.reload();
                    return;
               });
            };
            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };
        }
    ]);