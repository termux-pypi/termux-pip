from ..utils import log_success, log_error, log_info
from ..config import IS_TERMUX
from importlib.util import find_spec
from pathlib import Path
import subprocess
import tempfile
import shutil
import uuid
import sys
import os

try:
    from wheel._commands.unpack import unpack
    from wheel._commands.pack import pack
except ImportError as e:
    unpack = ...
    pack = ...

TERMUX_PREFIX = Path(os.environ.get('PREFIX', '/data/data/com.termux/files/usr'))
TERMUX_LIB_DIR = TERMUX_PREFIX / 'lib'
EXCLUDE_PREFIXES = (
    'libc.so', 'libdl.so', 'libm.so', 'liblog.so', 'libz.so', 'libc++_shared.so',
    'libandroid-support.so', 'libpython3', 'libcrypto.so', 'libssl.so', 'libffi.so',
    'libX11.so', 'libxcb.so', 'libGL.so', 'libtermux-exec.so', 'libiconv.so', 'libandroid-shmem.so'
)

def _patchelf(args: list[str]):
    try:
        return subprocess.run(['patchelf', '--page-size', '16384', *args], capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        return ''

def run_repair(wheel_path: str, output_dir: str = '.'):
    if not IS_TERMUX:
        log_error('Termux environment not detected. tpip must be run inside Termux or termux-docker.')
        sys.exit(1)

    if not all(find_spec(name) for name in ['wheel']):
        log_error('Missing dependencies for repair. Run: pip install tpip[build]')
        sys.exit(1)

    wheel_file = Path(wheel_path)
    log_info(f'Starting repair for: {wheel_file.name}')

    output_dir = Path(output_dir).resolve() if output_dir else wheel_file.parent
    output_dir.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        unpack(str(wheel_file), tmp_dir)
        unpacked_path = next(Path(tmp_dir).iterdir())
        libs_dir = unpacked_path / f"{wheel_file.name.split('-')[0]}.libs"

        extensions = list(unpacked_path.rglob('*.so'))
        if not extensions:
            if output_dir.resolve() == wheel_file.resolve().parent:
                log_info('No compiled extensions found. Original wheel is kept.')
            else:
                log_info('No compiled extensions found. Copying original wheel to destination...')
                shutil.copy2(wheel_file, output_dir)
            return str(output_dir / wheel_file.name)

        queue = extensions.copy()
        copied_libs = {}

        while queue:
            current_so = queue.pop(0)
            needed_libs = _patchelf(['--print-needed', str(current_so)]).split('\n')

            for lib in filter(None, needed_libs):
                if lib.startswith(EXCLUDE_PREFIXES):
                    continue

                termux_path = TERMUX_LIB_DIR / lib
                if termux_path.exists():
                    if lib not in copied_libs:
                        libs_dir.mkdir(exist_ok=True)
                        file_hash = uuid.uuid4().hex[:8]
                        if '.so' in lib:
                            prefix, suffix = lib.split('.so', 1)
                            hashed_name = f"{prefix}-{file_hash}.so{suffix}"
                        else:
                            hashed_name = f"{termux_path.stem}-{file_hash}{termux_path.suffix}"

                        dest_path = libs_dir / hashed_name
                        shutil.copy2(termux_path, dest_path)
                        _patchelf(['--set-soname', hashed_name, str(dest_path)])
                        copied_libs[lib] = hashed_name

                        log_info(f'Bundled: {lib} -> {hashed_name}')
                        queue.append(dest_path)
                    _patchelf(['--replace-needed', lib, copied_libs[lib], str(current_so)])

        if copied_libs:
            for so_file in unpacked_path.rglob('*.so'):
                rel_path = os.path.relpath(libs_dir, so_file.parent)
                new_rpath = '$ORIGIN' if rel_path == '.' else f'$ORIGIN/{rel_path}'
                old_rpaths = _patchelf(['--print-rpath', str(so_file)]).split(':')

                final_rpath = ':'.join(dict.fromkeys([new_rpath] + [p for p in old_rpaths if p]))
                _patchelf(['--set-rpath', final_rpath, str(so_file)])
            log_info('Repacking wheel...')
            pack(str(unpacked_path), output_dir, None)
            log_success(f'Repaired! Saved to {output_dir}')
            return str(output_dir / wheel_file.name)
        else:
            if output_dir.resolve() == wheel_file.resolve().parent:
                log_info('No external libraries required. Original wheel is kept.')
            else:
                log_info('No external libraries required. Copying original wheel to destination...')
                shutil.copy2(wheel_file, output_dir)
            return str(output_dir / wheel_file.name)
