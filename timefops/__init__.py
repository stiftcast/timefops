__author__ == "stiftcast"
__license__ == "GPLv3"
__version__ == "0.2"

TRANSLATIONS = {"atime": "access-time",
                "ctime": "change-time",
                "mtime": "modified-time"}

from .timefops import archive, copy, move
