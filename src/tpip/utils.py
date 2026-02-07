from .config import Colors
import subprocess
import sys


def log_info(message: str):
    print(f'{Colors.OKBLUE}[INFO]{Colors.ENDC} {message}')


def log_success(message: str):
    print(f'{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {message}')


def log_error(message: str):
    print(f'{Colors.FAIL}[ERROR]{Colors.ENDC} {message}', file=sys.stderr)


def run_command(command, shell=False):
    try:
        # check=True makes error, when command return != 0
        subprocess.run(command, shell=shell, check=True, text=True)
    except subprocess.CalledProcessError as e:
        log_error(f'Command failed: {command}')
        type(e)  # Remove IDE warnings
        sys.exit(1)
