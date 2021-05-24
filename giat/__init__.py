"""

"""

import sys

import click
import colorama
from colorama import Back
from colorama import Fore
from colorama import Style

from giat import giatcli


def main() -> None:
    try:
        colorama.init()
        if (sys.version_info.major, sys.version_info.minor) < (3, 8):
            click.echo(
                f"{Fore.RED}current is {sys.version},\n"
                f"{Back.WHITE}Please upgrade to >=3.8.{Style.RESET_ALL}")
            sys.exit()
        #######################################################################
        # giat action ...
        giatcli.giat()
    finally:
        colorama.deinit()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        sys.stderr.write(f"Error:{str(e)}\n")
        sys.exit(1)
