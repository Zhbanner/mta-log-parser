"""

Copyright::
    +===================================================+
    |                 © 2019 Privex Inc.                |
    |               https://www.privex.io               |
    +===================================================+
    |                                                   |
    |        Postfix Log Parser / Web UI                |
    |                                                   |
    |        Core Developer(s):                         |
    |                                                   |
    |          (+)  Chris (@someguy123) [Privex]        |
    |                                                   |
    +===================================================+

"""
from collections import namedtuple
from typing import List, Dict

import pytz
import json

from os import getenv as env, path as path, listdir as listdir
from dotenv import load_dotenv
from privex.helpers import env_bool, env_csv, env_int

load_dotenv()

DEBUG = env_bool('DEBUG', False)

vue_debug = env_bool('VUE_DEBUG', False)
"""
If True, the development version of Vue (with devtools support and logging) will be used instead of the 
production minified version.
"""

rethink_host = env('RETHINK_HOST', 'localhost')
rethink_port = int(env('RETHINK_PORT', 28015))
rethink_db = env('RETHINK_DB', 'maildata')

rethink_tables = [
    ('sent_mail', ['mail_to', 'timestamp', 'first_attempt', 'last_attempt']),
]

mail_domain = env('MAIL_DOMAIN', '')

mail_log_path = env('MAIL_LOG_PATH', '/var/log')
mail_log_filename = env('MAIL_LOG_FILENAME', 'mail.log')

mail_log = mail_log_path+'/'+mail_log_filename

admin_pass = env('ADMIN_PASS', 'SetThis!InYourEnv')
secret_key = env('SECRET_KEY', 'SetThis!InYourEnv')

# add prefix var from env
path_prefix = env('PATH_PREFIX', '')

# add housekeeping_days var from env
housekeeping_days = env_int('HOUSEKEEPING_DAYS', '')

# add datetime_format var from env
datetime_format = env('DATETIME_FORMAT', 'HH:mm:ss, DD.MM.YYYY')

# add mta var from env
mta = env('MTA', '')

log_timezone = pytz.timezone(env('LOG_TIMEZONE', 'UTC'))
"""
If your mail.log isn't in UTC, set the LOG_TIMEZONE env var to a pytz compatible timezone
"""

ignore_domains = env_csv('IGNORE_DOMAINS', ['localhost', '127.0.0.1'])

default_limit = env_int('DEFAULT_LIMIT', 50)
max_limit = env_int('MAX_LIMIT', 1000)

AppError = namedtuple('AppError', 'code message status', defaults=['', 500])
_ERRORS: List[AppError] = [
    AppError('UNKNOWN_ERROR', "An unknown error has occurred. Please contact the administrator of this site.", 500),
    AppError('NOT_FOUND', "The requested resource or URL was not found. You may wish to check the URL for typos.", 404),
    AppError('METHOD_NOT_ALLOWED', "This API endpoint does not allow the requested HTTP method (GET/POST/PUT etc.)", 405),
]
ERRORS: Dict[str, AppError] = {err.code: err for err in _ERRORS}
DEFAULT_ERR: AppError = ERRORS['UNKNOWN_ERROR']

# get all locale lang files
basedir = path.abspath(path.dirname(__file__))
lang_files = listdir(path.join(basedir,'static/locales/'))
new_lang_files_json = {}

for lang in lang_files:
    f = open(path.join(basedir,'static/locales/')+lang)
    data = json.load(f)
    before, sep, after = lang.partition('.')
    lang = before
    new_lang_files_json[lang] = data['locale_lang']

lang_files = json.dumps(new_lang_files_json)
