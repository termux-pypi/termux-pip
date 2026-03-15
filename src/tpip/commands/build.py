from ..utils import log_info, log_error
from .wheel import download, unpack
from ..tools.recipes import Recipes
from importlib.util import find_spec
from ..config import IS_TERMUX
from typing import Optional
import subprocess
import tempfile
import sys
import os


def run_build(path: str, wheel_dir: Optional[str] = None):
    if not IS_TERMUX:
        log_error('Termux environment not detected. tpip must be run inside Termux or termux-docker.')
        sys.exit(1)

    if not all(find_spec(name) for name in ['yaml']):
        log_error('Missing dependencies for build. Run: pip install tpip[build]')
        sys.exit(1)

    recipe = Recipes.get(path)
    log_info(f'Starting build process for: {recipe['metadata']['name']}=={recipe['metadata']['version']}')

    wheel_dir = wheel_dir or os.getcwd()
    with tempfile.TemporaryDirectory() as tmp_dir:
        wheel = download(
            recipe['metadata']['name'],
            recipe['metadata']['download_version'],
            output=tmp_dir
        )
        if wheel is False:
            log_info('No source code or wheel found for this package in PyPI.')
            sys.exit(1)
        if wheel.endswith('.whl'):
            log_info('Build system currently does not support .whl')
            sys.exit(1)
        unpacked = unpack(wheel, tmp_dir)
        source_code = os.path.join(unpacked, f'{recipe['metadata']['name']}-{recipe['metadata']['download_version']}')

        log_info('Checking for system dependencies...')

        system_dependencies = recipe['build']['system_dependencies']
        if system_dependencies:
            log_info(f'Installing: {', '.join(system_dependencies)}')

            try:
                command = ['pkg', 'install', '-y'] + system_dependencies
                subprocess.run(command, check=True)
                log_info('System dependencies installed.')
            except subprocess.CalledProcessError:
                log_error('Failed to install system packages. Check your internet connection')
                sys.exit(1)
        else:
            log_info('No system dependencies to install.')

        if recipe['build']['patches']:
            log_info(f'Applying {len(recipe['build']['patches'])} patches via git...')
            for patch, content in recipe['build']['patches'].items():
                log_info(f'Applying patch: {patch}')
                try:
                    subprocess.run(
                        ['git', 'apply'],
                        cwd=source_code,
                        input=content,
                        text=True,
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    log_error(f'Patch {patch} failed to apply: \n{e.output}')
                    sys.exit(1)
        else:
            log_info('No patches found for this recipe.')

        build_env = os.environ.copy()
        build_env.update(recipe['build']['env'])

        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'wheel', source_code, '--verbose', '--no-deps', '--wheel-dir', output_dir],
                check=True,
                env=build_env
            )
        except subprocess.CalledProcessError:
            log_error(f'Failed to build {recipe['metadata']['name']}=={recipe['metadata']['download_version']}')
