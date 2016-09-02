/*global angular, window*/

/**
 * @ngdoc service
 * @name MyBankApp.Utils
 * @description
 * # Utils
 * Service in the MyBankApp.
 */
angular.module('utils')
    .service('Utils', ['$cookieStore', '$rootScope', 'toaster', '$modal',
        function ($cookieStore, $rootScope, toaster, $modal) {
            'use strict';
            this.check_response = function (result) {
                if (result.data === null && result.status === 0) {
                    toaster.error('Server is down. Please try after some time');
                    return;
                }
                if (result.status !== 200 || result.data.response.status === 'error') {
                    var errorMessage;
                    try {
                        errorMessage = result.data.response.error;
                    } catch (e) {
                        // do nothing
                    } finally {
                        if (!errorMessage) {
                            errorMessage = result.status + ' ' + result.statusText;
                        }
                    }
                    toaster.error(errorMessage);
                    if (result.data.response.error.toLowerCase().indexOf('authorized') > -1 ||
                            result.data.response.error.toLowerCase().indexOf('authentication') > -1) {
                        $cookieStore.remove('USER_SSID');
                        var redirectUrl;
                        if (window.location.href.indexOf('/login') === -1) {
                            $rootScope.loggedIn = false;
                            if (window.location.href.indexOf('#') !== -1) {
                                redirectUrl = window.location.href.split('#')[1];
                            }
                            if (redirectUrl) {
                                window.location.replace(window.location.protocol + '//' + window.location.host + '/login' + '?redirect_url=' + redirectUrl);
                            } else {
                                window.location.replace(window.location.protocol + '//' + window.location.host + '/login');
                            }
                        }
                    }
                    return;
                }
                return result;
            };
            this.checkFailResponse = function (response) {
                return this.check_response(response);
            };
            // AngularJS will instantiate a singleton by calling "new" on this function
            this.extractImgSrc = function (html) {
                // extract first img url present in the html, if present
                if (html) {
                    var re = /<img\s+src=\"(.*?)[\?\"]/i;
                    if (html.search(re) > -1) {
                        return re.exec(html)[1];
                    }
                }
            };

            this.toAppId = function (categories) {
                //Translates app selections to a list of app IDs
                var result = [],
                    app_category = {
                        'google': {
                            'books': 60001,
                            'business': 60002,
                            'education': 60005,
                            'entertainment': 60006,
                            'games': 60008,
                            'music': 60015,
                            'weather': 60026
                        },
                        'apple': {
                            'books': 60501,
                            'business': 60502,
                            'education': 60503,
                            'entertainment': 60504,
                            'games': 60506,
                            'music': 60510,
                            'weather': 60521
                        }
                    };
                /*jslint unparam:true */
                angular.forEach(categories, function (values, app_store) {
                    angular.forEach(values, function (app_id, category) {
                        if (categories[app_store][category]) {
                            result.push(app_category[app_store][category]);
                        }
                    });
                });
                /*jslint unparam:false */
                return result;
            };

            this.fromAppId = function (categories) {
                var app_category = {
                        60001: {0: 'google', 1: 'books'},
                        60002: {0: 'google', 1: 'business'},
                        60005: {0: 'google', 1: 'education'},
                        60006: {0: 'google', 1: 'entertainment'},
                        60008: {0: 'google', 1: 'games'},
                        60015: {0: 'google', 1: 'music'},
                        60026: {0: 'google', 1: 'weather'},
                        60501: {0: 'apple', 1: 'books'},
                        60502: {0: 'apple', 1: 'business'},
                        60503: {0: 'apple', 1: 'education'},
                        60504: {0: 'apple', 1: 'entertainment'},
                        60506: {0: 'apple', 1: 'games'},
                        60510: {0: 'apple', 1: 'music'},
                        60521: {0: 'apple', 1: 'weather'}
                    },
                    result = {
                        'google': {
                            'books': false,
                            'business': false,
                            'education': false,
                            'entertainment': false,
                            'games': false,
                            'music': false,
                            'weather': false
                        },
                        'apple': {
                            'books': false,
                            'business': false,
                            'education': false,
                            'entertainment': false,
                            'games': false,
                            'music': false,
                            'weather': false
                        }
                    };
                angular.forEach(categories, function (x) {
                    if (x in app_category) {
                        var store_name = app_category[x][0],
                            category_name = app_category[x][1];
                        result[store_name][category_name] = true;
                    }
                });
                return result;
            };

            // Converting to the format so that filter can be applied.
            this.adapt_geo_info_to_other_Services_format = function (geo_info) {
                var out_geo_info = {};
                angular.forEach(geo_info, function (geo_arr) {
                    out_geo_info[geo_arr.id] = geo_arr.text;
                });
                return out_geo_info;
            };

            this.modal = function (template, cntrl, resolver) {
                return $modal.open({
                    templateUrl: template,
                    controller: cntrl,
                    resolve: resolver
                });
            };

            this.objToList = function (obj) {
                // Converts input object to a list of {id: xx, text: yy} objects.
                var result = [], id;
                for (id in obj) {
                    if (obj.hasOwnProperty(id)) {
                        result.push({'id': parseInt(id, 10), 'text': obj[id]});
                    }
                }
                return result;
            };

            this.listToObj = function (list) {
                // Converts list of objects with numeric values to an object.
                var result = {}, obj;
                for (obj in list) {
                    if (list.hasOwnProperty(obj)) {
                        result[list[obj].id] = parseFloat(list[obj].text);
                    }
                }
                return result;
            };

            this.multiplierModal = function (data, isValueEditable) {
                var that = this,
                    resolveBy = {
                        isEditable: function () {
                            return isValueEditable;
                        },
                        multipliers: function () {
                            return that.objToList(data);
                        }
                    };
                return this.modal('campaign/appNexus/multiplier.html', 'MultiplierCtrl', resolveBy);
            };

            this.findNameFromId = function (list, id) {
                var item;
                // Converts Id to text using provided mapping as list of {id: x, text: y} or {id: x, name: y} objects.
                for (item in list) {
                    if (list.hasOwnProperty(item) && list[item].id === id) {
                        if (list[item].text) {
                            return list[item].text;
                        }
                        return list[item].name;
                    }
                }
            };
        }]);

angular.module('utils')
    .directive('multiSepNgList', function() {
        'use strict';
        return {
            require: 'ngModel',
            link: function (scope, elem, attrs, ngModelCtrl) {
                var defaultSep = ', ', list,
                    format = function(value) {
                        if (angular.isArray(value)) {
                            return value.join(defaultSep);
                        }
                    },
                    parse = function(viewValue) {
                        list = [];
                        if (! viewValue) {
                            return list;
                        }
                        angular.forEach(viewValue.split(separator), function(value) {
                            if (value) {
                                list.push(value);
                            }
                        });
                        return list;
                    },
                    separator = new RegExp(attrs.multiSepNgList);
                ngModelCtrl.$parsers.push(parse);
                ngModelCtrl.$formatters.push(format);
            }
        };
    });
