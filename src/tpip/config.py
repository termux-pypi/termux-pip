import os

IS_TERMUX = '/com.termux' in os.environ.get('PREFIX', '')

TERMUX_PYPI_URL = 'https://termux-pypi.github.io/index/'

# Path to the config file
PIP_CONFIG_DIR = os.path.expanduser('~/.config/pip')
PIP_CONFIG_FILE = os.path.join(PIP_CONFIG_DIR, 'pip.conf')


# Colors for output in console
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
