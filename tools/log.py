"""Logger instances used across the project"""

import json
import logging

from os.path import join
from logging import config
from logstash_formatter import LogstashFormatterV1

import settings

LOG_DIR = join(settings.CURR_DIR, 'logs')
LOG_CONF = join(settings.CONFIG_DIR, 'log.ini')

# TODO: Use dictConfig instead
config.fileConfig(
    LOG_CONF, defaults={
        'count': settings.LOG_BACKUP_COUNT,
        'db_dump': settings.DB_BACKUP_FILE,
        'db_setup': settings.DB_BACKUP_FILE + '.db_setup',
        'log_file': join(LOG_DIR, 'bank.log'),
        'when': settings.LOG_ROTATE_WHEN,
    })

if settings.LOG_SQL_STATEMENTS:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# TODO Explore and add Tornado logs to the log file as well

logger = logging.getLogger('app')

handler = logging.FileHandler(join(LOG_DIR, 'bank.log.json'))
formatter = LogstashFormatterV1(
    fmt=json.dumps({
        'extra': {'app': settings.APP_NAME, 'env': settings.ENVIRONMENT}}))

handler.setFormatter(formatter)
logger.addHandler(handler)

# db dump logger
db_dump_logger = logging.getLogger('dbdump')

# db setup logger
db_logger = logging.getLogger('dbsetupdump')
