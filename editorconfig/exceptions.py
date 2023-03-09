"""EditorConfig exception classes

Licensed under Simplified BSD License (see LICENSE.BSD file).

"""

import os


class EditorConfigError(Exception):
    """Parent class of all exceptions raised by EditorConfig"""


try:
    from ConfigParser import ParsingError as _ParsingError
except:
    from configparser import ParsingError as _ParsingError


class ParsingError(_ParsingError, EditorConfigError):
    """Error raised if an EditorConfig file could not be parsed"""


class PathError(ValueError, EditorConfigError):
    """Error raised if invalid filepath is specified"""


class VersionError(ValueError, EditorConfigError):
    """Error raised if invalid version number is specified"""


class InvalidValue(EditorConfigError):
    """Raised when a key has a invalid value"""
    def __init__(self, path: str, message: str, key: str, value: str) -> None:
        self.path: str = path
        "The path to the file"

        self.message: str = message
        "A message that describes the problem"

        self.key: str = key
        "The key with the invalid value"

        self.value: str = value
        "The invalid value"

        super().__init__(f"{os.path.abspath(path)}: {message}")
