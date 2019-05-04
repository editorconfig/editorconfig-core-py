#!/usr/bin/env python3

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from editorconfig.fnmatch import translate

# MAIN

if len(sys.argv) != 3:
    print("Usage: create_re_utest <glob-expression> <expected-regular-expression>");
    sys.exit(1)

glob = sys.argv[1]
expected = sys.argv[2]
regex = translate(glob)

rc = 0

if regex is None or regex == "":
    print("ERROR: Can't translate \"%s\"\n", glob);
    rc = 3
elif regex != expected:
    print("ERROR: \"%s\" Expected: \"%s\" Got: \"%s\"\n" % (glob, expected, regex))
    rc = 2

sys.exit(rc)
