import platform
import os

def get_current_arch() -> str:
    machine = platform.machine().lower()

    if machine == 'aarch64':
        return 'aarch64'
    elif machine.startswith('arm'):
        return 'arm'
    elif machine == 'x86_64':
        return 'x86_64'
    elif machine in ('i386', 'i686', 'x86'):
        return 'i686'
    return machine
