"""Database tables."""
import json
import re
import traceback

from collections import defaultdict
from datetime import datetime
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String,
    Text)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from tornado.options import define, options

from tools.utils import DATE_FORMAT, DATETIME_FORMAT, load_json
from tools.exceptions import InvalidInputError
from tools.log import logger

define("db_debug", type=bool)
define("db_path", type=str)
define("charset", type=str, group='db')
define("collation", type=str, group='db')
define("db_name", type=str, group='db')
define("dialect", type=str, group='db')
define("host", type=str, group='db')
define("passwd", type=str, group='db')
define("user", type=str, group='db')

define('mybank_map', default='mybank.json',
       help='DB columns and request JSON fields mapping')

MYBANK_MAP = load_json(options.mybank_map)

VERY_SHORT = 20
SHORT = 45
MEDIUM = 100
LARGE = 1000


def from_dict(obj, values, strict=True):
    """Update DB model object with values from input dictionary. Raises error
    if readonly field is passed unless strict is False."""
    def get_val(col, json_key, values):
        """Map the DB column to key in request JSON and get its value. Do a
        dump if column is of JSON type. Finds key in nested dictionaries."""
        try:
            values = values[json_key]
        except KeyError:
            key_chain = json_key.split('.')
            for _key in key_chain:
                values = values[_key]
        if strict and hasattr(col, 'read_only') and values:
            logger.info('Skipping field %s as it is read-only', col)
            return None
        if hasattr(col, 'is_json'):
            return json.dumps({json_key: values})
        if not values:
            return
        if isinstance(col.type, DateTime):
            return datetime.strptime(values, DATETIME_FORMAT)
        if isinstance(col.type, Date):
            try:
                values = datetime.strptime(values, DATE_FORMAT)
            except (TypeError, ValueError):
                try:
                    values = datetime.strptime(values, DATETIME_FORMAT)
                except (TypeError, ValueError):
                    logger.error("Unable to convert data to timestamp")
                    logger.error(traceback.format_exc())
                    return None
        return values

    if not isinstance(values, dict):
        raise InvalidInputError('Expected dictionary. Found %s' % type(values))

    for col in obj.__table__.columns:
        json_key = MYBANK_MAP.get(str(col))
        if json_key is None:
            continue
        try:
            setattr(obj, col.name, get_val(col, json_key, values))
        except KeyError:
            continue


def to_dict(obj, map=None):
    """Method to get dictionary from a DB model."""
    def get_val(json_key, col):
        """Get model value. Do a load if a JSON field. Else raise error."""
        val = getattr(obj, col.name)
        if not val:
            return val
        if isinstance(col.type, DateTime):
            val = val.strftime(DATETIME_FORMAT)
        if isinstance(col.type, Date):
            val = val.strftime(DATE_FORMAT)
        if hasattr(col, 'is_json'):
            try:
                val = json.loads(val).get(json_key)
            except ValueError as e:
                logger.error("Invalid JSON found in column %s", col)
                raise e
            except KeyError:
                raise
        return val
    if map is None:
        map = MYBANK_MAP
    for col in obj.__table__.columns:
        col_str = str(col)
        # TODO: uncomment the code and fetch profile_id, creatives_id from db
        # if col_str in ['creatives.id', 'targeting_profile.id']:
        #     continue
        json_key = map.get(col_str)
        if not json_key:
            continue
        val = get_val(json_key, col)
        if '.' in json_key:
            # TODO Review this code block
            key_chain = json_key.split('.')
            temp = defaultdict(dict)
            for _key in key_chain[:-1]:
                temp = temp[_key]
            val, temp[key_chain[-1]] = temp, val
            json_key = key_chain[0]
        yield json_key, val


class CustomColumn(Column):
    """Tagged column"""
    def __init__(self, *args, **kwargs):
        opts = ['is_json', 'read_only']
        for opt in opts:
            if args and opt in args:
                setattr(self, opt, True)
                args = list(args)
                args.remove(opt)
                args = tuple(args)
            if kwargs and kwargs.get(opt):
                setattr(self, opt, True)
                kwargs.pop(opt)
        super(CustomColumn, self).__init__(*args, **kwargs)


class JSONColumn(CustomColumn):
    """Column that stores JSON text"""
    def __init__(self, *args, **kwargs):
        super(JSONColumn, self).__init__('is_json', *args, **kwargs)


class ReadOnlyColumn(CustomColumn):
    """Column that should not be modified by clients"""
    def __init__(self, *args, **kwargs):
        super(ReadOnlyColumn, self).__init__(*args, read_only=True, **kwargs)


def camel_to_snake(name):
    """Converts CamelCase to camel_case
    >>> camel_to_snake('CamelCase')
    'camel_case'
    >>> camel_to_snake('CamelCamelCase')
    'camel_camel_case'
    >>> camel_to_snake('Camel2Camel2Case')
    'camel2_camel2_case'
    >>> camel_to_snake('getHTTPResponseCode')
    'get_http_response_code'
    >>> camel_to_snake('get2HTTPResponseCode')
    'get2_http_response_code'
    >>> camel_to_snake('HTTPResponseCode')
    'http_response_code'
    >>> camel_to_snake('HTTPResponseCodeXYZ')
    'http_response_code_xyz'
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class Custom(object):
    """Custom base class used by all models"""
    @declared_attr
    def __tablename__(cls):         # pylint: disable=E0213
        return camel_to_snake(cls.__name__)

    id = ReadOnlyColumn(Integer, primary_key=True)

    from_dict = from_dict
    to_dict = to_dict
    __iter__ = to_dict              # makes dict(model) work


class Timestamped(object):
    """Mix-in class for adding change-tracking attributes"""
    last_modified = Column(DateTime)

    # For relations columns we do require declared_attr decorator
    @declared_attr
    def last_modified_by(cls):      # pylint: disable=E0213,R0201
        """Adds last modified by column to every table."""
        return Column(Integer, ForeignKey('user.id'))


Base = declarative_base(cls=Custom)

class Counter(Base):
    """Stores counters of different tables"""
    __tablename__ = 'counter'
    id = CustomColumn(Integer, primary_key=True)
    name = CustomColumn(String(100), unique=True)
    value = CustomColumn(Integer)

class User(Base, Timestamped):
    """Stores users and their tokens."""
    user_name = Column(String(MEDIUM), unique=True)
    first_name = Column(String(MEDIUM))
    middle_name = Column(String(MEDIUM))
    last_name = Column(String(MEDIUM))
    display_name = Column(String(MEDIUM))
    password_hash = Column(String(MEDIUM))
    transaction_password_hash = Column(String(MEDIUM))
    pan = Column(String(MEDIUM))
    adhar_number = Column(String(MEDIUM))
    mobile_number = Column(String(MEDIUM))
    mail = Column(String(MEDIUM), unique=True)
    account_id = Column(String(MEDIUM), unique=True)
    status = Column(String(VERY_SHORT), default='active')
    created_at = CustomColumn(DateTime, default=datetime.now)

class UserToken(Base):
    """Stores users and their tokens."""
    user_id = Column(Integer, ForeignKey('user.id'))
    token = Column(String(MEDIUM), unique=True)
    token_ts = Column(DateTime, default=datetime.now)


class Account(Base):
    account_id = Column(String(MEDIUM), ForeignKey('user.account_id'))
    account_name = Column(String(MEDIUM), ForeignKey('user.user_name'))
    type = Column(Enum('SAVING', 'CURRENT'), default='SAVING')
    balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey('user.id'))

class Transaction(Base, Timestamped):
    transaction_id = Column(String(MEDIUM), unique=True)
    account_id = Column(String(MEDIUM), ForeignKey('account.account_id'))
    description = Column(String(LARGE))
    type = Column(Enum('CREDITED', 'DEPOSITED'))
    amount = Column(Float)
    total = Column(Float)
    created_at = CustomColumn(DateTime, default=datetime.now)

class Payee(Base, Timestamped):
    user_id = Column(Integer, ForeignKey('user.id'))
    account_id = Column(String(MEDIUM), unique=True)
    account_name = Column(String(MEDIUM))
    nick_name = Column(String(MEDIUM))
    bank = Column(String(MEDIUM))
    ifsc_code = Column(String(MEDIUM))
    type = Column(Enum('INTERNAL', 'NEFT', 'IMPS'), default='INTERNAL')
    added_at = CustomColumn(DateTime, default=datetime.now)


