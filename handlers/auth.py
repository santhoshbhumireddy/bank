"""Handler class for user authentication"""

import json
from datetime import datetime
from time import time
from tornado.web import url
from sqlalchemy import func

from handlers.base import BaseHandler
from settings import (
    APP_ABBR, APP_BASE_URL, ENVIRONMENT, ACCOUNT_COUNTER_START, ENCRYPTION_KEY,
    BRANCH_CODE, BANK_CODE, USER_SESSION_EXPIRE_TIME)
from tools.exceptions import AuthError
from tools.models import (Account, Counter, User, UserToken)
from tools.services.db_api import DatabaseAPI
from tools.utils import generate_hash, encode

class Auth(BaseHandler):
    """Handler for user authentication"""
    def _authenticate_user(self):
        """Skip authentication by overriding"""

    def _authorize_user(self):
        """Skip authorization by overriding"""

    def _track_change(self, resp):
        """Skip track change by overriding"""

    def post(self):
        """Checks user authentication"""
        auth_body = self.request.body['auth']
        user_name = auth_body.get('user_name')
        password = auth_body.get('password')
        password_hash = encode(ENCRYPTION_KEY, password)
        with DatabaseAPI() as db_obj:
            user = db_obj.db_session.query(User). \
                filter(User.user_name == user_name).first()
            if not user:
                return {"status": "error", "error": 'User not Registered'}
            elif user.password_hash != password_hash:
                return {"status": "error", "error": "Invalid Credentials"}
            cookie = generate_hash()
            cookie_expire_time = int(time() + USER_SESSION_EXPIRE_TIME)
            resp = {"status": "ok", "user_info": dict(user),
                    "authentication_token": cookie}
            user_token_obj = db_obj.create_obj(
                UserToken, user_id=user.id, token=cookie, token_ts=datetime.now())
            db_obj.insert_or_update(user_token_obj)
        self.set_secure_cookie(
            'USER_SSID',
            json.dumps({"cookie": cookie, "expires_in": cookie_expire_time}),
            expires=cookie_expire_time)
        return resp


class Register(BaseHandler):
    """Handler for user Register"""

    def _authenticate_user(self):
        """Skip authentication by overriding"""

    def _authorize_user(self):
        """Skip authorization by overriding"""

    def post(self):
        """User Registration"""
        user_info = self.request.body['user_info']
        with DatabaseAPI() as db_obj:
            user = db_obj.db_session.query(User). \
                filter(User.user_name == user_info['user_name']).first()
            if user:
                return {"status": "error",
                        "error": 'This User already existed'}
            else:
                user = User()
            user.from_dict(user_info)
            user.password_hash = encode(
                ENCRYPTION_KEY, user_info['password'])
            user.transaction_password_hash = encode(
                ENCRYPTION_KEY, user_info['transaction_password'])
            counter = db_obj.db_session.query(Counter). \
                filter(Counter.name == User.__tablename__).first()
            if not counter:
                counter = Counter()
                counter.name = User.__tablename__
                # Account ID  starts from 100000
                counter.value = ACCOUNT_COUNTER_START
            user.account_id = str(BANK_CODE) + str(BRANCH_CODE) + str(counter.value)
            counter.value += 1
            db_obj.insert_or_update(counter)
            id = db_obj.insert_or_update(user, 'id')
            user.id = id
            account = Account()
            account.user_id = user.id
            account.account_id = user.account_id
            account.account_name = user.user_name
            account_id = db_obj.insert_or_update(account, 'id')
            resp = {"status": "ok", "user_info": dict(user)}
        return resp


handlers = [
    url(r'/auth', Auth),
    url(r'/register', Register),
]


if __name__ == "__main__":
    pass
