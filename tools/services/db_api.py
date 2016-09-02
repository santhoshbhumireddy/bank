#!/usr/bin/env python

"""Exposes database related operations"""

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import scoped_session, sessionmaker
from tornado.options import options, parse_config_file

from settings import APP_CONF
from tools.models import Base
from tools.exceptions import InvalidColumnError, InvalidInputError

parse_config_file(APP_CONF)
engine = None

POOL_SIZE = 20


def get_engine(db_path=None):
    """Create and return engine. If db_path is not given, settings in
    app.conf are used"""
    global engine
    if not engine:
        if not db_path:
            db_path = options.db_path % options.group_dict('db')
        engine = create_engine(
            db_path,
            convert_unicode=True,
            echo=options.db_debug,
            pool_size=POOL_SIZE)
    return engine


class DatabaseAPI(object):
    """Context manager for automatically closing database session"""
    def __init__(self, db_path=None):
        self.db_path = db_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_api.db_session.close()

    def __enter__(self):
        class DatabaseAPIResource(object):
            """API for database related operations"""
            def __init__(self, db_path):
                self.engine = get_engine(db_path)
                self.db_session = self.init_db_session()

            def create_tables(self):
                """Create tables"""
                Base.metadata.create_all(bind=self.engine)

            def init_db_session(self):
                """Create and engine"""
                return scoped_session(sessionmaker(bind=self.engine))

            def get_objs(self, model, **attr_map):
                """Returns all objects matching attribute map"""
                return self.get_obj(model, first=False, **attr_map)

            def get_obj(self, model, first=True, **attr_map):
                """Returns first object of the model with columns and their
                values from the mapping. If first flag is False, returns all
                matched objects.
                """
                try:
                    objs = self.db_session.query(model).filter_by(**attr_map)
                except InvalidRequestError as e:
                    # FIXME: Use InvalidColumnError instead
                    raise InvalidInputError(e.message)
                if objs.count():
                    if first:
                        return objs.first()
                    return objs

            @staticmethod
            def create_obj(model, strict=False, **attr_map):
                """Creates and returns an object with values set from the
                mapping. Mapping may have keys which are not columns of the
                model. However, if strict flag is set, mapping can't have
                keys which are not columns of the model.

                Note: Method doesn't insert record in table. You need
                to invoke insert_or_update method to enter the record.
                """
                obj = model()
                for col, val in attr_map.iteritems():
                    if hasattr(obj, col):
                        setattr(obj, col, val)
                    elif strict:
                        raise InvalidColumnError(obj.__tablename__, col)
                return obj

            def get_or_create(self, model, first=True, **attr_map):
                """Returns first object of the model with columns and their
                values from the mapping. If first flag is False, returns all
                matched objects.
                If no match found, creates and returns an object with values
                set from the mapping. Mapping must not have keys which are not
                columns of the model.

                Note that the create doesn't insert record in table. You need
                to invoke insert_or_update method to enter the record.
                """
                objs = self.get_obj(model, first, **attr_map)
                if objs:
                    return objs
                # strict is always True here to create a model instance.
                # Otherwise, query will have to handle every invalid property.
                strict = True
                return self.create_obj(model, strict, **attr_map)

            def insert_or_update(self, obj, pkey=None):
                """Inserts or updates model object"""
                if hasattr(obj, 'last_modified'):
                    obj.last_modified = datetime.now()
                obj = self.db_session.merge(obj)
                self.db_session.commit()
                if not pkey:
                    return
                if hasattr(obj, pkey):
                    return getattr(obj, pkey)
                else:
                    raise InvalidColumnError(obj.__tablename__, pkey)

            def bulk_insert_or_update(self, objs):
                """Insert or update multiple objects at a time"""
                for obj in objs:
                    self.db_session.merge(obj)
                self.db_session.commit()

            def del_obj(self, model, **pkeys):
                """Deletes row from the table"""
                obj = self.db_session.query(model)
                for col, val in pkeys.items():
                    model_col = getattr(model, col)
                    obj = obj.filter(model_col == val)
                obj.delete()
                self.db_session.commit()

        self.db_api = DatabaseAPIResource(self.db_path)
        return self.db_api
