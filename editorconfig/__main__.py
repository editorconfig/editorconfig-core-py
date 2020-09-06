"""EditorConfig command line interface

Licensed under Simplified BSD License (see LICENSE.BSD file).

"""

from __future__ import absolute_import, print_function, unicode_literals

import getopt
import sys

from . import VERSION, __version__
from .compat import force_unicode
from .exceptions import ParsingError, PathError, VersionError
from .handler import EditorConfigHandler
from .versiontools import split_version


def version():
    print("EditorConfig Python Core Version {}".format(__version__))


def usage(command, error=False):
    out = sys.stderr if error else sys.stdout
    print("{} [OPTIONS] FILENAME\n".format(command), file=out)
    print("-f                 "
          'Specify conf filename other than ".editorconfig".\n', file=out)
    print("-b                 "
          "Specify version (used by devs to test compatibility).\n", file=out)
    print("-h OR --help       Print this help message.\n", file=out)
    print("-v OR --version    Display version information.\n", file=out)


def main():
    command_name = sys.argv[0]
    try:
        opts, args = getopt.getopt(list(map(force_unicode, sys.argv[1:])),
                                   "vhb:f:", ["version", "help"])
    except getopt.GetoptError as e:
        print(str(e))
        usage(command_name, error=True)
        sys.exit(2)

    version_tuple = VERSION
    conf_filename = '.editorconfig'

    for option, arg in opts:
        if option in ('-h', '--help'):
            usage(command_name)
            sys.exit()
        if option in ('-v', '--version'):
            version()
            sys.exit()
        if option == '-f':
            conf_filename = arg
        if option == '-b':
            version_tuple = split_version(arg)
            if version_tuple is None:
                sys.exit("Invalid version number: {}".format(arg))

    if not args:
        usage(command_name, error=True)
        sys.exit(2)
    filenames = args
    multiple_files = len(args) > 1

    for filename in filenames:
        handler = EditorConfigHandler(filename, conf_filename, version_tuple)
        try:
            options = handler.get_configurations()
        except (ParsingError, PathError, VersionError) as e:
            print(str(e))
            sys.exit(2)
        if multiple_files:
            print("[{}]".format(filename))
        for key, value in options.items():
            print("{}={}".format(key, value))


if __name__ == "__main__":
    main()
