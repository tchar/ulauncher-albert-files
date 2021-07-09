import os
from collections import UserString
from ..result import Result

class CacheEntry(UserString):
        def __init__(self, path, root_entry, is_directory=False):
            super().__init__(path)
            self.name = os.path.basename(path)
            self.path = path
            self.basename, self.ext = os.path.splitext(self.name)
            self.path_len = path.count(os.sep)

            if root_entry is None: relpath = ''
            else: relpath = os.path.relpath(path, root_entry.path)
            self.relpath = relpath
            self.relpath_basename, _ = os.path.splitext(self.relpath)
            self.relpath_len = relpath.count(os.sep)
            
            self.root_entry = root_entry
            self.is_directory = is_directory

            self.name_lower = self.name.lower()
            self.basename_lower = self.basename.lower()
            self.relpath_lower = self.relpath.lower()
            self.relpath_basename_lower = self.relpath_basename.lower()

        def to_result(self, score=None):
            return Result(self.path, self.is_directory, score)
