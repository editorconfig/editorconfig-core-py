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

setup(
    name='EditorConfig',
    version=version,
    author='EditorConfig Team',
    packages=['editorconfig'],
    url='http://editorconfig.org/',
    license='python',
    description='EditorConfig File Locator and Interpreter for Python',
    long_description=open('README.rst').read(),
    entry_points = {
        'console_scripts': [
            'editorconfig = editorconfig.__main__:main',
        ]
    },
    classifiers=[
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
