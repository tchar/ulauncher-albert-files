import os
import re
from pathspec import PathSpec
import fnmatch
from pathspec.patterns import GitWildMatchPattern
from . import logging

class Ignore:
    IGNORE_FILENAME = None
    _logger = logging.getLogger(__name__)

    def __init__(self, pathspec, match_str):
        self.match_str = match_str
        self._pathspec = pathspec

    @classmethod
    def set_ignore_filename(cls, ignore_filename):
        cls.IGNORE_FILENAME = ignore_filename
    
    def should_include(self, value):
        return self(value)

    def __call__(self, value):
        if self._pathspec is None or self.match_str == '':
            return True
        return not self._pathspec.match_file(value)

    @staticmethod
    def get_root_matcher():
        return Ignore(None, '')

    @staticmethod
    def get_matcher(directory, file_names, parent_matcher):
        if Ignore.IGNORE_FILENAME not in file_names:
            return parent_matcher or Ignore.get_root_matcher()
        try:
            albertignore_path = os.path.join(directory, Ignore.IGNORE_FILENAME)
            with open(albertignore_path, 'r') as f:
                match_str = f.read()
        except Exception as e:
            Ignore._logger('Got exception when reading ignore file {}: {}'.format(albertignore_path, e))
            return parent_matcher or Ignore.get_root_matcher()
        try:
            if parent_matcher.match_str:
                match_str = parent_matcher.match_str + '\n' + match_str
            pathspec = PathSpec.from_lines(GitWildMatchPattern, match_str.splitlines())
        except Exception as e:
            Ignore._logger('Got exception when creating pathspec matcher with str {}: {}'.format(match_str, e))
            return parent_matcher or Ignore.get_root_matcher()
        
        return Ignore(pathspec, match_str)


class Match:
    def __init__(self, value):
        value = value.strip()
        if not value:
            self._matcher = None
            self._matcher_ignorecase = None
            return
        value = fnmatch.translate(value)
        self._matcher = re.compile(value)
        self._matcher_ignorecase = re.compile(value, flags=re.IGNORECASE)

    def matches(self, value):
        if not self._matcher:
            return False
        return self._matcher.match(value) is not None

    def matches_ignorecase(self, value):
        if not self._matcher_ignorecase:
            return False
        return self._matcher_ignorecase.match(value) is not None

    def __call__(self, value, ignorecase=False):
        return self.matches(value) if not ignorecase else self.matches_ignorecase(value)
