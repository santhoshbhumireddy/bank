"""Application settings file."""

# Note: Before adding anything here, ask yourself if the system administrator
# would ever need to change it.

from os.path import abspath, dirname, join

CURR_DIR = abspath(dirname(__file__))
CONFIG_DIR = join(CURR_DIR, 'config')
BACKUP_DIR = join(CURR_DIR, 'backup')

DB_BACKUP_FILE = join(BACKUP_DIR, 'bank.sql')
DB_BACKUP_COUNT = 30
DB_METADATA_FILE = join(BACKUP_DIR, 'bank.sql.metadata')


# Application config file.
APP_CONF = join(CONFIG_DIR, 'app.conf')

LOG_SQL_STATEMENTS = True
LOG_BACKUP_COUNT = 45
LOG_ROTATE_WHEN = "midnight"

APP_ABBR = 'BANK'
ENVIRONMENT = 'local'
ENVIRONMENT = ENVIRONMENT.upper()
APP_NAME = 'BankAPP'

APP_BASE_URL = "http://localhost:9889"
APP_VERSION = "0.0.1"

# User session expiry in seconds
USER_SESSION_EXPIRE_TIME = 1800


BANK_CODE = 800
BRANCH_CODE = 043
ACCOUNT_COUNTER_START = 100000

ENCRYPTION_KEY = 'mysecret'