import re
from pathlib import Path
from typing import Any

class SecurityError(Exception):
    """Raised when security validation fails"""
    pass


def validate_package_name(name: str) -> None:
    """Validate package name according to PEP 508"""
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$', name):
        raise SecurityError(f'Invalid package name: {name}')
    if '..' in name or '/' in name or '\\' in name:
        raise SecurityError(f'Path traversal attempt in package name: {name}')

def validate_version(version: str) -> None:
    """Validate version string"""
    if not re.match(r'^[a-zA-Z0-9._+-]+$', version):
        raise SecurityError(f'Invalid version string: {version}')
    if '..' in version or '/' in version or '\\' in version:
        raise SecurityError(f'Path traversal attempt in version: {version}')


def validate_system_dependencies(deps: list[str]) -> None:
    """Validate system dependencies are safe"""
    for dep in deps:
        if not re.match(r'^[a-z0-9_-]+$', dep):
            raise SecurityError(f'Invalid package name format: {dep}')



def validate_recipe(recipe: dict[str, Any]) -> None:
    """Validate entire recipe structure"""
    validate_package_name(recipe['metadata']['name'])
    validate_version(recipe['metadata']['version'])
    validate_version(recipe['metadata']['download_version'])

    if recipe['build']['system_dependencies']:
        validate_system_dependencies(recipe['build']['system_dependencies'])

