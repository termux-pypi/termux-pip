import re
from pathlib import Path
from typing import Any

ALLOWED_ARCHES = frozenset({'aarch64', 'arm', 'x86_64', 'i686'})


class SecurityError(Exception):
    """Raised when security validation fails"""
    pass


def validate_package_name(name: str) -> None:
    """Validate package name according to PEP 508"""
    if not isinstance(name, str) or not re.fullmatch(r'[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?', name):
        raise SecurityError(f'Invalid package name: {name}')
    if '..' in name or '/' in name or '\\' in name:
        raise SecurityError(f'Path traversal attempt in package name: {name}')

def validate_version(version: str) -> None:
    """Validate version string"""
    if not isinstance(version, str) or not re.fullmatch(r'[a-zA-Z0-9._+-]+', version):
        raise SecurityError(f'Invalid version string: {version}')
    if '..' in version or '/' in version or '\\' in version:
        raise SecurityError(f'Path traversal attempt in version: {version}')


def validate_system_dependencies(deps: list[str]) -> None:
    """Validate system dependencies are safe (no leading '-', so they can't act as pkg/apt options)"""
    if not isinstance(deps, list):
        raise SecurityError('system_dependencies must be a list')
    for dep in deps:
        if not isinstance(dep, str) or not re.fullmatch(r'[a-z0-9][a-z0-9+.-]*', dep):
            raise SecurityError(f'Invalid package name format: {dep}')


def validate_env(env: dict[str, str]) -> None:
    """Structural check only: the content of env is intentionally not restricted"""
    if not isinstance(env, dict):
        raise SecurityError('env must be a mapping')
    for key, value in env.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise SecurityError(f'env keys and values must be strings: {key!r}')


def validate_pip_args(args: list[str]) -> None:
    """Structural check only: the content of pip_args is intentionally not restricted"""
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        raise SecurityError('pip_args must be a list of strings')


def validate_exclude_arches(arches: list[str]) -> None:
    if not isinstance(arches, list):
        raise SecurityError('exclude_arches must be a list')
    for arch in arches:
        if arch not in ALLOWED_ARCHES:
            raise SecurityError(f'Unknown architecture in exclude_arches: {arch}')


def validate_patch_path(patch: str, recipe_dir: Path | str | None = None) -> None:
    """Patch files must live inside the recipe directory"""
    if not isinstance(patch, str) or not patch:
        raise SecurityError(f'Invalid patch path: {patch!r}')
    path = Path(patch)
    if path.is_absolute() or '..' in path.parts:
        raise SecurityError(f'Patch path must be relative and inside the recipe directory: {patch}')
    if recipe_dir is not None:
        base = Path(recipe_dir).resolve()
        if not (base / path).resolve().is_relative_to(base):
            raise SecurityError(f'Patch path escapes the recipe directory: {patch}')


def validate_recipe(recipe: dict[str, Any], recipe_dir: Path | str | None = None) -> None:
    """Validate entire recipe structure"""
    if not isinstance(recipe, dict):
        raise SecurityError('Recipe must be a mapping')
    metadata = recipe.get('metadata')
    build = recipe.get('build')
    if not isinstance(metadata, dict) or not isinstance(build, dict):
        raise SecurityError("Recipe must contain 'metadata' and 'build' sections")

    for key in ('name', 'version', 'download_version'):
        if key not in metadata:
            raise SecurityError(f'Missing metadata field: {key}')

    validate_package_name(metadata['name'])
    validate_version(metadata['version'])
    validate_version(metadata['download_version'])

    def optional(key: str, default):
        value = build.get(key)
        return default if value is None else value

    validate_system_dependencies(optional('system_dependencies', []))
    validate_env(optional('env', {}))
    validate_pip_args(optional('pip_args', []))
    validate_exclude_arches(optional('exclude_arches', []))

    patches = optional('patches', [])
    if not isinstance(patches, list):
        raise SecurityError('patches must be a list')
    for patch in patches:
        validate_patch_path(patch, recipe_dir)
