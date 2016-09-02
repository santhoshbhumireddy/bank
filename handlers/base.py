"""Base Handler class for the application.

Other handler classes inherit from this class. Add common methods and
properties here.
"""
import tornado.ioloop
import tornado.web

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial, wraps
from json import dumps, loads
from pytz import timezone
from time import time
from tornado.web import RequestHandler
from tornado.web import HTTPError
from types import MethodType

from settings import USER_SESSION_EXPIRE_TIME

from tools.exceptions import (
    AuthError, InvalidInputError, SimultaneousEditError)
from tools.log import logger
from tools.models import User, UserToken
from tools.services.db_api import DatabaseAPI
from tools.utils import DATETIME_FORMAT, to_class

APP_VERSION = '0.0.1'
AUTH_TIME_OUT = 'Authentication timed out'
VALID_METHODS = ('DELETE', 'GET', 'POST', 'PUT')
HTTP_CODE = {
    'unauthorized': 401,
    'bad_request': 400,
    'server_error': 500
}

EXECUTOR = ThreadPoolExecutor(max_workers=4)
IQT_EXECUTOR = ThreadPoolExecutor(max_workers=1)


def unblock(f):
    """ Non-blocking decorator """
    @tornado.web.asynchronous
    @wraps(f)
    def wrapper(*args, **kwargs):
        """Wrapper for methds to be non-blocking"""
        self = args[0]

        def callback(future):
            """Async's callback after completion"""
            self.set_header('Content-Type', 'application/json')
            self.write(future.result())
            self.flush()
            self.finish()

        if "Metadata" in str(self):
            IQT_EXECUTOR.submit(
                partial(f, *args, **kwargs)
            ).add_done_callback(
                lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                    partial(callback, future)))
        else:
            EXECUTOR.submit(
                partial(f, *args, **kwargs)
            ).add_done_callback(
                lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                    partial(callback, future)))
    return wrapper


class BaseHandler(RequestHandler):
    """Parent class of handlers. Supports CRUD operations

    Performs operations common to all the requests.
    """

    def prepare(self, long_running=False, methods=None):
        """
        Wraps the verb methods with a decorated one that performs all common
        operations.
        :param long_running: Indicate if the operation takes a lot of time
        :param methods: Specify the verb methods that are long running as a
         list of verb strings. If none is passed, all verb methods (get, put,
         post...) are assumed to be long running.
        :return: None
        """
        self.methods = methods
        self.long_running = long_running
        if self.request.method in VALID_METHODS:
            self._decorate_method()

    @property
    def geo_jsons_cache(self):
        """Property to access geo JSONs cache"""
        return self.application.geo_jsons_cache

    def _decorate_method(self):
        """Decorate CRUD method.

        Performs common operations by decorating CRUD method dynamically.
        """
        method_name = self.request.method.lower()
        if hasattr(self.__class__, method_name):
            regular_method = getattr(self.__class__, method_name)
            if self.long_running and (
                    not self.methods or method_name in self.methods):
                enhanced_method = self._perform_common_async(regular_method)
            else:
                enhanced_method = self._perform_common_ops(regular_method)

            # Add a bound method to the current instance
            setattr(self, method_name, MethodType(enhanced_method, self))

    def _json_to_dict(self):
        """Converts request body from JSON to dictionary"""
        if not self.request.body:
            self.request.body = {}
            return
        try:
            self.request.body = loads(self.request.body)
        except (TypeError, ValueError) as e:
            raise InvalidInputError(e.message)

    def _authenticate_user(self):
        """Authenticate and extend user session"""
        val = self.get_secure_cookie('USER_SSID')
        if not val:
            raise AuthError(AUTH_TIME_OUT)
        val = loads(val)
        cookie = val['cookie']
        with DatabaseAPI() as db_obj:
            user = db_obj.get_obj(UserToken, token=cookie)
        if not user:
            raise AuthError(AUTH_TIME_OUT)
        delta = int(time() - val['expires_in'])
        cookie_expire_time = time() + USER_SESSION_EXPIRE_TIME
        if delta >= 0:
            raise AuthError(AUTH_TIME_OUT)
        else:
            # Extend user session
            self.set_secure_cookie(
                'USER_SSID',
                dumps({"cookie": cookie, "expires_in": cookie_expire_time}),
                expires=cookie_expire_time)
            # Add user info to the headers
            with DatabaseAPI() as db_obj:
                user_obj = db_obj.get_obj(User, id=user.user_id)
                self.current_user = user_obj
        if self.request.method == 'PUT' or self.request.method == 'POST':
            # Update last_modified
            self.request.body[self.request.body.keys()[0]].update({
                'last_modified_by': user.user_id})

    def _authorize_user(self):
        """Check if user is authorized to make this request"""
        pass

    def _check_simultaneous_edit(self):
        """Check if the user is working with stale data"""
        if self.request.method != 'PUT':
            return
        ui_dict = self.request.body
        model, key = None, None
        for key in ui_dict.iterkeys():
            model = to_class(key)
            break
        if not model or not key:
            return
        last_modified = ui_dict[key].get('last_modified')
        if not last_modified:
            return
        last_modified = datetime.strptime(last_modified, DATETIME_FORMAT)
        model_id = ui_dict[key]['id']
        with DatabaseAPI() as db_obj:
            obj = db_obj.get_obj(model, id=model_id)
            if not obj or not obj.last_modified or\
                    last_modified == obj.last_modified:
                return
            user = db_obj.get_obj(User, id=obj.last_modified_by)
            secs = (obj.last_modified - last_modified).total_seconds()
            raise SimultaneousEditError(
                'This %s has been modified by %s user %d seconds ago,'
                'please refresh before save' % (key, user.display_name, secs))

    @staticmethod
    def _update_username(resp):
        """Replace user id with user display name in the response dict"""
        if not resp:
            return
        key = resp.keys()[0]
        if not isinstance(resp[key], dict) or\
                not resp[key].get('last_modified_by'):
            return
        user_id = resp[key].get('last_modified_by')
        try:
            with DatabaseAPI() as db_obj:
                user = db_obj.get_obj(User, id=user_id)
                if not user:
                    return
                name = user.display_name if user.display_name else user.mail
                resp[key]['last_modified_by'] = name
        except Exception as e:
            logger.error(e.message, exc_info=True)

    @staticmethod
    def _perform_common_ops(func):
        """Decorator to perform common operations like authentication,
        authorization, check simultaneous edit etc."""
        def perform_ops(self, *args, **kwargs):
            """perform common operations"""
            self._core_method(func, *args, **kwargs)
            self.set_header('Content-Type', 'application/json')
            self.write(self.content)
        return perform_ops

    @staticmethod
    def _perform_common_async(func):
        """Decorator to perform common operations like authentication,
        authorization, check simultaneous edit etc."""
        @unblock
        def perform_ops(self, *args, **kwargs):
            """perform common operations"""
            self._core_method(func, *args, **kwargs)
            return self.content
        return perform_ops

    def _core_method(self, func, *args, **kwargs):
        """Performs common operations"""
        self.content = {
            "response": {"status": "ok"},
            "service": {"version": APP_VERSION}}
        try:
            if self.request.uri == '/auth':
                # request.body contains password; don't log it
                logger.info(
                    '%s %s', self.request.method, self.request.uri)
            else:
                logger.info(
                    '%s %s %s', self.request.method, self.request.uri,
                    self.request.body)
            self._json_to_dict()
            self._authenticate_user()
            self._authorize_user()
            self._check_simultaneous_edit()
            resp = func(self, *args, **kwargs)
            # self._update_username(resp)
            if resp:
                self.content.get("response").update(resp)
        except AuthError as e:
            logger.info(e.message)
            self.set_status(HTTP_CODE['unauthorized'])
            self.content.get("response").update(
                {"status": "error", "error": e.message})
        except HTTPError as e:
            logger.error(e.message, exc_info=True)
            self.set_status(e.status_code)
            self.content.get("response").update(
                {"status": "error", "error": str(e.message)})
        except Exception as e:
            logger.error(e.message, exc_info=True)
            self.set_status(HTTP_CODE['server_error'])
            self.content.get("response").update(
                {"status": "error",
                 "error": e.__class__.__name__ + ": " + str(e)})
        else:
            pass