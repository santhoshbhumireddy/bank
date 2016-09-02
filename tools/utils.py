"""Utility classes used across the project"""

import base64
import requests
import inspect
import urllib
import urllib2

from datetime import datetime, timedelta
from hashlib import sha1
from json import dumps, load
from os.path import join
from pyotp import TOTP
from random import randint

import settings

from settings import CONFIG_DIR
from tools.exceptions import InvalidInputError

# Date format
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_MICRO_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
OTP_SECRET_KEY = 'base32secret3232'

def returnResponseToHandler(func):
    """Decorator to create custom Response objects."""
    def customize_response(self, *args, **kwargs):
        """Return or create custom response."""
        resp = func(self, *args, **kwargs)
        if isinstance(resp, requests.models.Response):
            return resp
        for key, val in resp.iteritems():
            if key != 'status':
                time_str = datetime.strftime(datetime.now(),
                    settings.DATETIME_MICRO_FORMAT)
                if isinstance(val, list):
                    for obj in val:
                        if isinstance(obj, dict):
                            obj['fetch_time'] = time_str
                elif isinstance(val, dict):
                    val['fetch_time'] = time_str
        content = {"response": {"status": ""},
                   "service": {"version": settings.APP_VERSION}}
        content.get("response").update(resp)
        return content
    return customize_response


def decorateClassMethods(dec_func, methods=[], action='include'):
    """Decorate methods of a class.

    :params: :include: Apply decorators to these function names.
    :params: :exclude: Do not apply decorators to these function names.
    """
    def decorate_class(cls, *args, **kwargs):
        """Decorating verb request methods of class."""
        for name, method in inspect.getmembers(cls, inspect.ismethod):
            decorate = False
            if action == 'include':
                if name in methods:
                    decorate = True
            elif action == 'exclude':
                if name not in methods:
                    decorate = True
            if decorate:
                setattr(cls, name, dec_func(method))
        return cls
    return decorate_class

def convert_timestamp_to_date(timestamp, date_format):
    """Converts timestamp to date string format."""
    return datetime.fromtimestamp(int(timestamp)).strftime(date_format)

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def convert_date_to_req_format(
        date_str, cur_format=DATE_FORMAT, req_format=DATETIME_FORMAT):
    """Converts date from present format to required format.

    Params:
        date_str: Date in string
        cur_format: Current format of the date_str
        req_format: Required format
    Returns:
        returns date in required format
    """
    date_obj = datetime.strptime(date_str, cur_format)
    return date_obj.strftime(req_format)

def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

def generate_hash():
    """Generates hash using the current time"""
    cur_date = datetime.now().strftime(DATETIME_MICRO_FORMAT)
    return sha1(cur_date).hexdigest()

def generate_otp():
    """Generates one time password"""
    totp = TOTP(OTP_SECRET_KEY)
    return totp.now()

def verify_otp(otp, generated_at):
    """Verifies generated OTP"""
    current_time = datetime.now()
    expiry_time = generated_at + timedelta(
        seconds=settings.OTP_EXPIRE_TIME)
    if current_time <= expiry_time:
        return True
    return False

def send_sms_otp(mobiles, message):
    sender = "COUMEN"
    route = 4

    values = {
        'authkey' : SMS_AUTH_KEY,
        'mobiles' : ','.join(mobiles),
        'message' : message.replace('\n', ' '),
        'sender' : sender,
        'route' : route,
	    'country': 91
    }
    postdata = urllib.urlencode(values)
    req = urllib2.Request(SMS_PROVIDER_URL, postdata)
    response = urllib2.urlopen(req)
    output = response.read()
    print output

def load_json(json_file, dir_path=CONFIG_DIR):
    """Loads json file."""
    try:
        with open(join(dir_path, json_file)) as f:
            return load(f)
    except ValueError as e:
        raise InvalidInputError(
            'Unable to load json file %s: %s', (json_file, e.message))


def to_class(tablename):
    """Return class reference mapped to table.

    :param tablename: String with name of table.
    :return: Class reference or None.
    """
    from tools.models import Base       # Avoid circular import
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c
