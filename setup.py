from setuptools import setup

import editorconfig

setup(
    name='EditorConfig',
    version=editorconfig.__version__,
    author='EditorConfig Team',
    packages=['editorconfig'],
    url='http://editorconfig.org/',
    license='python',
    description='EditorConfig File Locator and Interpreter for Python',
    long_description=open('README.rst').read(),
    entry_points = {
        'console_scripts': [
            'editorconfig = editorconfig.main:main',
        ]
    },
    classifiers=[
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
