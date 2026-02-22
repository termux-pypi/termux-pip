from ..config import RECIPES_MAIN_URL
from ..utils import log_error
from typing import TypedDict, Optional
from urllib.parse import urljoin
from pathlib import Path
import sys
import os

try:
    import httpx
    import yaml
except ImportError as e:
    httpx = ...
    yaml = ...

Versions = dict[str, list[str]]
Patches = dict[str, str] | list[str]


class Recipes:
    def __init__(self, is_local: bool = False) -> None:
        self.url: str = RECIPES_MAIN_URL
        self.is_local = is_local

    def _get_patches(self, recipe: TypedRecipe, link: Optional[str] = None, path: Optional[str] = None) -> Patches:
        loaded_patches = {}
        try:
            for patch in recipe['build']['patches']:
                match self.is_local:
                    case True:
                        patch_path = patch
                        if path:
                            patch_path = os.path.join(path, patch)

                        with open(patch_path) as f:
                            loaded_patches[patch] = f.read()
                    case False:
                        patch_link = urljoin(link, patch) if link else (
                            f'{self.url}/recipes/{recipe['metadata']['name']}/{recipe['metadata']['version']}/{patch}'
                        )
                        response = httpx.get(patch_link)
                        response.raise_for_status()
                        loaded_patches[patch] = response.text
        except Exception as e:
            log_error(f'Error getting patches for {recipe['metadata']['name']}=={recipe['metadata']['version']}: {e}')
            sys.exit(1)
        return loaded_patches

    def get(self, package: str, version: str) -> TypedRecipe:
        try:
            response = httpx.get(f'{self.url}/recipes/{package}/{version}/recipe.yaml')
            response.raise_for_status()
            recipe: TypedRecipe = yaml.safe_load(response.text)
            recipe['build']['patches'] = self._get_patches(recipe)
            return recipe
        except Exception as e:
            log_error(f'Error getting recipe.yaml for {package}=={version}: {e}')
            sys.exit(1)

    def load_packages(self) -> Versions:
        try:
            response = httpx.get(f'{self.url}/versions.json')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log_error(f'Error downloading versions.json: {e}')
            sys.exit(1)

    @classmethod
    def from_string(cls, link_or_file: str) -> TypedRecipe:
        instance = cls()
        if Path(link_or_file).is_file():
            with open(link_or_file) as f:
                recipe: TypedRecipe = yaml.safe_load(f.read())
            recipe_dir = str(Path(link_or_file).parent.resolve())
            instance.is_local = True
            recipe['build']['patches'] = instance._get_patches(recipe, path=recipe_dir)
            return recipe
        elif link_or_file.startswith('http'):
            response = httpx.get(link_or_file)
            response.raise_for_status()
            recipe: TypedRecipe = yaml.safe_load(response.text)
            instance.is_local = False
            recipe['build']['patches'] = instance._get_patches(recipe, link=link_or_file)
            return recipe
        # get package from termux-pypi, coming soon:
        # if package_name not in packages:
        #     log_error(f'Package wasn\'t found in our recipes: {package_name}')
        #     sys.exit(1)
        #
        # if not version:
        #     log_info('Version wasn\'t provided. We will use latest version from our recipes')
        #     version = max(packages[package_name], key=parse)
        #
        # if version and version not in packages[package_name]:
        #     log_info(
        #         f'{package_name}=={version} isn\'t available in our recipes. We will try to build it without patches...'
        #     )
        log_error(f'Unable to read recipe: {link_or_file}. Please, insert link or path to the recipe')
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
