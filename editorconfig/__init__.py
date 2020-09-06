"""EditorConfig Python Core"""

from editorconfig.version import VERSION
from editorconfig.versiontools import join_version

__all__ = ['get_properties', 'EditorConfigError', 'exceptions']

__version__ = join_version(VERSION)


def get_properties(filename):
    """Locate and parse EditorConfig files for the given filename"""
    handler = EditorConfigHandler(filename)
    return handler.get_configurations()


from editorconfig.exceptions import *
from editorconfig.handler import EditorConfigHandler
