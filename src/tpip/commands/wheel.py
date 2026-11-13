from ..utils import log_success
from typing import Optional
from pathlib import Path
import shutil
import os

try:
    from unearth import PackageFinder
    from unearth.evaluator import Package
except ImportError as e:
    PackageFinder = ...
    Package = ...


def download(package_name: str, version: str, wheel_dir: str = None, prefer: str = 'wheel'):
    """Download a distribution from PyPI.

    prefer='wheel': a pure-python (none-any) wheel wins over the sdist.
    prefer='sdist': only the sdist is considered (used by `tpip build`).
    """
    finder = PackageFinder(
        index_urls=['https://pypi.org/simple/'],
        no_binary=[package_name] if prefer == 'sdist' else [],
    )
    matches = finder.find_best_match(f'{package_name}=={version}')

    distribution_package: Optional[Package] = None
    for pkg in matches.applicable:
        filename = pkg.link.filename
        if not filename.endswith('.whl'):
            distribution_package = pkg
            if prefer == 'sdist':
                break
            continue
        if prefer == 'wheel' and 'none-any.whl' in filename:
            distribution_package = pkg
            break

    if distribution_package:
        target_dir = wheel_dir if wheel_dir else os.getcwd()
        wheel_file = str(finder.download(distribution_package.link, target_dir))
        log_success(f'Downloaded: {wheel_file}')
        return wheel_file
    return False


def unpack(file_path: str, output_dir: str = None):
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f'File not found: {file_path}')

    match path.suffix:
        case '.whl':
            if not output_dir:
                output_dir = path.name.split('.whl')[0]
            shutil.unpack_archive(file_path, output_dir, format='zip')
        case '.gz':
            if not output_dir:
                output_dir = path.name.split('.tar.gz')[0]
            shutil.unpack_archive(file_path, output_dir, filter='data')
        case _:
            raise ValueError(f'Unsupported format: {path.name}')
    return Path(output_dir).resolve()