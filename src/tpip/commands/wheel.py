from typing import Optional
from pathlib import Path
import shutil
import os

try:
    from pypi_simple import PyPISimple, DistributionPackage, tqdm_progress_factory
except ImportError as e:
    PyPISimple = ...
    DistributionPackage = ...
    tqdm_progress_factory = ...


def download(package_name: str, version: str, output: str = None):
    with PyPISimple() as pypi:
        package = pypi.get_project_page(package_name)

        matches_version = [package for package in package.packages if package.version == version]

        distribution_package: Optional[DistributionPackage] = None
        for pkg in matches_version:
            if pkg.package_type == 'sdist':
                distribution_package = pkg
                continue
            if pkg.package_type == 'wheel':
                if 'none-any.whl' in pkg.filename:
                    distribution_package = pkg
                    break

        if distribution_package:
            if output:
                output = os.path.join(output, distribution_package.filename)
            else:
                output = os.path.join(os.getcwd(), distribution_package.filename)

            pypi.download_package(
                distribution_package, path=output, progress=tqdm_progress_factory()
            )
            print(output)
            return output
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
            shutil.unpack_archive(file_path, output_dir)
        case _:
            raise ValueError(f'Unsupported format: {path.name}')
    return Path(output_dir).resolve()
