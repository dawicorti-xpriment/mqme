import sys
import os
import tempfile

if not hasattr(sys, 'frozen'):
    APP_PATH = os.path.dirname(__file__)
    sys.path.append(os.path.join(APP_PATH, 'src'))
else:
    APP_PATH = os.path.dirname(sys.executable)

APP_NAME = 'MQME'
VERSION = '0.8.4'
IMAGES_PATH = os.path.abspath(os.path.join(
    APP_PATH, 'assets', 'images'
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

try:
    os.makedirs(TMP_PATH)
except:
    pass
