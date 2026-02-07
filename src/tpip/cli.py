from .commands.setup import run_setup
from .commands.build import run_build
from tpip import __version__
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog='tpip',
        description='Termux-optimized wheel installer and builder'
    )
    # version
    parser.add_argument('-v', '--version', action='version', version=f'tpip {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # setup
    subparsers.add_parser('setup', help='Configure pip to use Termux-PyPI index')

    # build
    # parser_build = subparsers.add_parser('build', help='Build a package with patches')
    # parser_build.add_argument('package', help='Name of the package to build (e.g., numpy)')

    args = parser.parse_args()

    match args.command:
        case 'setup':
            run_setup()
        case 'build':
            run_build(args.package)
        case _:
            parser.print_help()
            sys.exit(1)


if __name__ == '__main__':
    main()
