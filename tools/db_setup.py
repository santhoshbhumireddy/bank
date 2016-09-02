#!/usr/bin/env python

"""DB maintenance script"""

import json
import subprocess

from argparse import ArgumentParser
from mysql.connector import MySQLConnection
from os.path import exists, join
from pickle import dump, load
from re import search
from sqlalchemy.exc import (
    DBAPIError, IntegrityError, OperationalError, ProgrammingError)
from time import time
from tornado.options import options, parse_config_file

from settings import APP_CONF, BACKUP_DIR, CONFIG_DIR
from tools.log import logger, db_logger
from tools.models import Base
from tools.services.db_api import DatabaseAPI
from tools.utils import to_class


parse_config_file(APP_CONF)

DB_CONFIG_KEYS = ["user", "passwd", "charset", "collation", "host"]

db_settings = {k: v for k, v in options.group_dict('db').items()
               if k in DB_CONFIG_KEYS}

AUTH_INIT = join(CONFIG_DIR, 'auth_init.json')


def initialize_roles(db_obj):
    """Initializes roles and related tables"""
    logger.info("Initializing authorization tables")
    auth_details = json.load(open(AUTH_INIT))
    logger.info("Populating roles table")
    for (id, role, description) in auth_details['roles']:
        record = Role(id=id, role=role, description=description)
        db_obj.insert_or_update(record)
    logger.info("Populating applications table")
    for (id, name, description) in auth_details['applications']:
        record = Application(id=id, name=name, description=description)
        db_obj.insert_or_update(record)
    logger.info("Populating permissions table")
    for (role_id, application_id, access_code) in auth_details['permissions']:
        record = Permission(
            role_id=role_id, application_id=application_id,
            access_code=access_code)
        db_obj.insert_or_update(record)


def recreate_db():
    """Drop and create DB using latest model definitions"""
    logger.debug(db_settings)
    db_obj = MySQLConnection(**db_settings)
    db_obj.connect()
    cursor = db_obj.cursor()
    drop_all = "DROP DATABASE IF EXISTS %s;"
    logger.info('Dropping database')
    cursor.execute(drop_all % options.db_name)
    db_settings.update({'db': options.db_name})
    logger.info('Creating database')
    cursor.execute(
        """CREATE DATABASE IF NOT EXISTS %(db)s
           DEFAULT CHARACTER SET %(charset)s
           DEFAULT COLLATE %(collation)s;""" % db_settings)
    cursor.close()
    with DatabaseAPI() as db_api:
        db_api.create_tables()


def insert_advertiser():
    """Temporary req."""
    logger.info('Creating advertiser table entry for WebMD')
    with DatabaseAPI() as db_api:
        advertiser = Advertiser()
        advertiser.name = 'WebMD'
        advertiser.id = WEBMD_ADVERTISER_ID
        db_api.insert_or_update(advertiser)


def query_model_during_export(db_obj, model):
    """Retrieves query for existing columns of the table modified.

     During DB setup, newly added column throw error on querying. Those
     columns need to be skipped while querying.

     Doesn't export deleted campaigns.

     Args:
        db_obj: instance of DatabaseAPI
        model: instance of DB table

    Returns:
        All the results of the query.
    """
    except_cols = list()
    tbl_name = model.__tablename__
    while True:
        try:
            rows = db_obj.db_session.query(
                *[c for c in model.__table__.c if c.name not in
                  except_cols])
            rows = rows.all()
        except (TypeError, OperationalError) as e:
            if 'Unknown database' in e.message:
                raise e
            logger.debug(e.message)
            col_name = search(r"%s\.(.+?)'" % tbl_name, e.message).group(1)
            logger.info("Skipping new column %s", col_name)
            except_cols.append(col_name)
        else:
            return rows


def export_tables():
    """Export all tables to a pickle"""
    with DatabaseAPI() as db_obj:
        for table in Base.metadata.tables.keys():
            export_table(db_obj, to_class(table))


def export_table(db_obj, model):
    """Dump rows of a table as pickle file.

    Args:
        db_obj: instance of DatabaseAPI
        model: instance of DB table
    """
    tbl_name = model.__tablename__
    logger.info("Exporting %s", tbl_name)
    file_name = tbl_name + '.pickle'
    # If a column is missing from database, likely as a result of a new column
    # just added, skip that column.
    try:
        rows = query_model_during_export(db_obj, model)
    except ProgrammingError as e:
        # New Table.
        logger.error(
            'Export failed for %s. Probably new table. Confirm message: %s',
            tbl_name, e.message)
        return
    result = []
    with open(join(BACKUP_DIR, file_name), "w") as fp:
        for row in rows:
            row_dict = row._asdict()
            result.append(row_dict)
        dump(result, fp)


def import_tables():
    """Import all tables from pickle"""
    all_tables = set(Base.metadata.tables.keys())
    dependent = _find_related_tables()
    with DatabaseAPI() as db_obj:
        # Import independent tables first
        for tablename in all_tables - set(dependent):
            import_table(db_obj, to_class(tablename))
        for tablename in dependent:
            import_table(db_obj, to_class(tablename))


def import_table(db_obj, model):
    """Does exactly as the name suggests"""
    tbl_name = model.__tablename__
    file_name = tbl_name + '.pickle'
    logger.info("Importing %s", tbl_name)
    try:
        now = time()
        with open(join(BACKUP_DIR, file_name)) as fp:
            rows = load(fp)
            logger.info("No. of rows: %s", len(rows))
            if not rows:
                logger.info("Nothing to import. Skipping table %s.", tbl_name)
                return
            logger.info("Inserting the rows of %s in bulk", tbl_name)
            try:
                objs = [model(**row) for row in rows]
                db_obj.bulk_insert_or_update(objs)
            except DBAPIError:
                db_obj.db_session.rollback()
                logger.error("Error while inserting rows in bulk,"
                             "now inserting sequentially")
                insert_sequential(rows, model)
            logger.info(
                'Completed in %0.3s seconds', (time() - now))
    except IOError as e:
        logger.error(
            "Importing %s failed. Probably a new table. Confirm message: %s",
            tbl_name, e.message)


def insert_sequential(rows, model):
    """Non-bulk insert of rows"""
    for row in rows:
        with DatabaseAPI() as db_obj:
            try:
                db_obj.insert_or_update(model(**row))
            except IntegrityError:
                # TODO write error records to another file
                db_obj.db_session.rollback()
                logger.info(
                    "Skipping import of %s row: %s", model.__tablename__, row)


def _find_related_tables():
    """Finds tables that are related with foreign key constraints. Both tables
    that are dependent and those that others depend on are returned. Tables
    are listed in the order of dependency: occurring earlier are independent of
    tables occurring later in the list."""
    ordered = []
    for name, table in Base.metadata.tables.items():
        if table.foreign_keys:
            # insert table after all the tables on which it depends
            max_index = 0
            # max_index tracks the maximum of the indices of dependent tables
            for key in table.foreign_keys:
                if key.column.table.name not in ordered:
                    ordered.insert(0, key.column.table.name)
                    max_index += 1      # a new dependent added, push over by 1
                else:
                    index = ordered.index(key.column.table.name)
                    if index >= max_index:
                        max_index = index + 1
            if name in ordered:
                index = ordered.index(name)
                if index < max_index:
                    ordered.remove(name)
                    max_index -= 1
                else:
                    continue
            ordered.insert(max_index, name)
    return ordered


def backup_db():
    """Export a fresh snapshot of the database"""
    db_logger.handlers[0].doRollover()     # log to a new file
    cmd = ["mysqldump", "-u", options.user, "-p" + options.passwd,
           options.db_name]
    try:
        export = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        db_logger.error("DB doesn't exist. Error: %s", e)
        return
    db_logger.info("%s", export)
    return export


def populate_geo_config():
    """Populate APN geo configuration JSON files if not present."""
    fetch_geo = False
    for type in GEO_TYPES.iterkeys():
        if not exists(join(APN_GEO_JSONS, 'all_' + type + '.json')):
            fetch_geo = True
            break
    if fetch_geo:
        fetch_write_apn_info()
        generate_postal_code_JSON()


def preserve_all():
    """Recreates database preserving all tables"""
    try:
        export_tables()
    except OperationalError:
        # If database doesn't exist then create new setup
        preserve_none_and_sync()
        return
    recreate_db()
    import_tables()
    # with DatabaseAPI() as db_obj:
    #     initialize_roles(db_obj)


def preserve_none_and_sync():
    """Recreating database without preserving existing data
    and syncing campaigns"""
    recreate_db()
    insert_advertiser()
    sync_segments()
    sync_creatives()
    sync_campaigns('apn_console')
    populate_geo_config()
    # with DatabaseAPI() as db_obj:
    #     initialize_roles(db_obj)


def parse_args():
    """Parse command line arguments"""
    ap = ArgumentParser(
        description="Recreates the database keeping data intact.")
    group = ap.add_mutually_exclusive_group()
    group.add_argument(
        "-r", "--rebuild", action="store_true",
        help="Recreate database, fetching fresh data from RTB")
    return ap.parse_args()


def main():
    """The main stuff"""
    args = parse_args()
    backup_db()
    if args.rebuild:
        preserve_none_and_sync()
    else:
        preserve_all()


if __name__ == '__main__':
    main()
