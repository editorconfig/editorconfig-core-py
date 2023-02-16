import os
from setuptools import setup

# Read the version
g = {}
with open(os.path.join("editorconfig", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    v = g['VERSION']
    version = ".".join(str(x) for x in v[:3])
    if v[3] != "final":
        version += "-" + v[3]

if __name__ == "__main__":
    setup(version=version)
