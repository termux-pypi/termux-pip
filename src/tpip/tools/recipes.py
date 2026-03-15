from __future__ import annotations
from ..config import RECIPES_MAIN_URL
from ..utils import log_error
from typing import TypedDict
from pathlib import Path
import sys
import os

try:
    import yaml
except ImportError as e:
    yaml = ...

Versions = dict[str, list[str]]
Patches = dict[str, str] | list[str]


class Recipes:
    def __init__(self) -> None:
        self.url: str = RECIPES_MAIN_URL

    def _get_patches(self, recipe: TypedRecipe, path: str) -> Patches:
        loaded_patches = {}
        try:
            for patch in recipe['build']['patches']:
                patch_path = patch
                if path:
                    patch_path = os.path.join(path, patch)

                with open(patch_path) as f:
                    loaded_patches[patch] = f.read()
        except Exception as e:
            log_error(f'Error getting patches for {recipe['metadata']['name']}=={recipe['metadata']['version']}: {e}')
            sys.exit(1)
        return loaded_patches

    def get(self, path: str) -> TypedRecipe:
        try:
            with open(path) as f:
                recipe: TypedRecipe = yaml.safe_load(f.read())
            recipe_dir = str(Path(path).parent.resolve())
            recipe['build']['patches'] = self._get_patches(recipe, recipe_dir)
            return recipe
        except Exception as e:
            log_error(f'Error loading recipe.yaml for {package}=={version}: {e}')
            sys.exit(1)


class TypedRecipe(TypedDict):
    metadata: MetadataInfo
    build: BuildInfo


class MetadataInfo(TypedDict):
    name: str
    version: str
    download_version: str


class BuildInfo(TypedDict):
    system_dependencies: list[str]
    env: dict[str, str]
    patches: Patches
