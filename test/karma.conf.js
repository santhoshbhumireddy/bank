// Karma configuration
// http://karma-runner.github.io/0.12/config/configuration-file.html
// Generated on 2014-11-08 using
// generator-karma 0.8.3

module.exports = function (config) {
    'use strict';

    config.set({
        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: true,

        // base path, that will be used to resolve files and exclude
        basePath: '../',

        frameworks: ['jasmine'],

        reporters: ['progress', 'coverage', 'junit'],

        coverageReporter: {
            type: 'cobertura',
            dir: 'test/reports',
            subdir: '.',
            file: 'angular-coverage.xml'
        },

        junitReporter: {
            outputFile: 'test/reports/angular-tests.xml'
        },

        preprocessors: {
            'app/**/!(*spec).js': ['coverage']
        },

        // list of files / patterns to load in the browser
        files: [
            // TODO: Find a generic way to do following.
            'bower_components/angular/angular.js',
            'bower_components/angular-mocks/angular-mocks.js',
            'bower_components/angular-cookies/angular-cookies.js',
            'bower_components/angular-resource/angular-resource.js',
            'bower_components/angular-route/angular-route.js',
            'bower_components/angular-sanitize/angular-sanitize.js',
            'bower_components/angular-ui-utils/ui-utils.js',
            'bower_components/angular-ui-select/dist/select.js',
            'bower_components/angular-bootstrap/ui-bootstrap-tpls.js',
            'bower_components/checklist-model/checklist-model.js',
            'bower_components/angular-notify-toaster/toaster.js',
            'bower_components/angular-local-storage/dist/angular-local-storage.js',
            'bower_components/ng-breadcrumbs/dist/ng-breadcrumbs.js',
            'bower_components/angular-animate/angular-animate.js',
            'bower_components/underscore/underscore.js',
            'bower_components/jquery/dist/jquery.js',
            'bower_components/ng-messages/angular-messages.js',
            'app/app.js',
            'app/**/*.js'
        ],

        // list of files / patterns to exclude
        exclude: [],

        // web server port
        port: 8080,

        browsers: [
            'PhantomJS'
        ],

        // Which plugins to enable
        plugins: [
            'karma-phantomjs-launcher',
            'karma-jasmine',
            'karma-coverage',
            'karma-junit-reporter'
        ],

        // Continuous Integration mode
        // if true, it capture browsers, run tests and exit
        singleRun: false,

        colors: true,

        // level of logging
        // possible values: LOG_DISABLE || LOG_ERROR || LOG_WARN || LOG_INFO || LOG_DEBUG
        logLevel: config.LOG_INFO,

        // Uncomment the following lines if you are using grunt's server to run the tests
        proxies: {
           '/': 'http://localhost:9000/'
        },
        // URL root prevent conflicts with the site root
        urlRoot: '_karma_'
    });
};
