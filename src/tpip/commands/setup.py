from ..config import TERMUX_PYPI_URL, IS_TERMUX
from ..utils import log_info, log_success, log_error
import subprocess
import sys


def run_setup():
    if not IS_TERMUX:
        log_error('Termux environment not detected. tpip must be run inside Termux or termux-docker.')
        return
    log_info('Checking existing pip configuration...')

    current_urls = get_current_extra_index()

    # Checking for Termux-PyPI in current config
    if TERMUX_PYPI_URL in current_urls:
        log_success('Termux-PyPI is already in your extra-index-url')
        return

    if current_urls:
        new_urls = f'{current_urls} {TERMUX_PYPI_URL}'
    else:
        new_urls = TERMUX_PYPI_URL

    log_info(f'Adding {TERMUX_PYPI_URL} to configuration...')

    # Set updated values
    set_cmd = [sys.executable, '-m', 'pip', 'config', 'set', 'global.extra-index-url', new_urls]

    try:
        subprocess.run(set_cmd, check=True, capture_output=True, text=True)
        log_success('Successfully updated pip configuration.')
        log_info(f'New extra-index-url list: {new_urls}')
    except subprocess.CalledProcessError as e:
        log_error(f'Failed to set config: {e.stderr}')


def get_current_extra_index():
    """Gets current pip config to return extra-index-urls"""
    cmd = [sys.executable, '-m', 'pip', 'config', 'get', 'global.extra-index-url']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        type(e)  # Remove IDE warning
        pass
    return ''
