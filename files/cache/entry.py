import os
from collections import UserString
from ..result import Result

class CacheEntry(UserString):
        def __init__(self, path, root_entry, is_directory=False):
            super().__init__(path)
            self.path = path
            self.root_entry = root_entry
            self.is_directory = is_directory
            self._path_len = None

        @property
        def path_len(self):
            if self._path_len is None:
                self._path_len = self.path.count(os.sep)
            return self._path_len

        @property
        def relative_path_len(self):
            if self.root_entry is None:
                return 0
            return self.path_len - self.root_entry.path_len

        def to_result(self, score=None):
            return Result(self.path, self.is_directory, score)

        # def __len__(self):
        #     return len(self.path)

        # def __hash__(self):
        #     return hash(self.path)

        # def __eq__(self, other):
        #     return isinstance(other, CacheEntry) and self.path == other.path

        # def __lt__(self, other):
        #     return isinstance(other, CacheEntry) and self.path < other.path

        # def __gt__(self, other):
        #     return not (self < other)

        # def __ge__(self, other):
        #     return isinstance(other, CacheEntry) and self.path <= other.path

        # def __le__(self, other):
        #     return isinstance(other, CacheEntry) and self.path >= other.path
