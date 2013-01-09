import sys
import os
import tempfile

APP_PATH = os.path.join(os.path.dirname(__file__), 'src')
APP_NAME = 'MQME'
VERSION = '0.1'
IMAGES_PATH = os.path.abspath(os.path.join(
    APP_PATH, '..', 'assets', 'images'
))
FULL_APP_NAME = '%s %s' % (APP_NAME, VERSION)
CONFIG_FILE_PATH = os.path.join(os.path.expanduser('~'), '.mqmerc')
TMP_PATH = os.path.join(tempfile.gettempdir(), 'mqme')
RESOLUTION = (800, 600)
QUEUE_READ_LOOP_DELAY = 200

# Fight environment preview periods (have to be modulo 25 ms)
FIGHTENV_SCROLL_PERIODS = {
    'background3': 100,
    'background2': 50,
    'background1': 25,
}

FIGHTENV_SCROLL_GAP = 0.02

sys.path.append(APP_PATH)

try:
    os.makedirs(TMP_PATH)
except:
    pass
