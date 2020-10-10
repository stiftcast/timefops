__all__ = ["Timefops"]
__author__ = "stiftcast"
__license__ = "GPLv3"
__version__ = "0.3"

TRANSLATIONS = {"atime": "access-time",
                "ctime": "change-time",
                "mtime": "modified-time"}

from .timefops import Timefops
