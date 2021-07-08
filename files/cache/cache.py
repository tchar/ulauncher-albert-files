import os
import re
from time import time
import math
import itertools
from threading import RLock
from .entry import CacheEntry
from .. import logging
from ..match import Ignore, Match
from ..result import Result
from ..utils import Singleton, lock

class Cache(metaclass=Singleton):
    SEARCH_TERM_REGEX = re.compile(r'([_\-])', flags=re.IGNORECASE)
    COMMON_EXTS = set([
        'txt', 'torrent', 'mp4', 'm3u', 'm4a', '3g2', '3gp', 'avi',
        'mpg', 'srt', 'gif', 'mp3', 'png', 'iso', 'py', 'js', 'zipx',
        'zip', 'tar', 'gz', '7z', 'rar', 'rpm', 'deb', 'pdf','doc',
        'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'tex', 'csv',
        'html', 'html'
    ])

    def __init__(self):
        self._search_after_characters = 2
        self._search_max_results = 5
        self._search_threshold = 0.5
        self._root_paths = ()
        self._depths = ()
        self._data = {}
        self._common_prefix = ''
        self._shortest_path = 0
        self._longest_path = 1
        self._lock = RLock()
        self._logger = logging.getLogger(__name__)

    @lock
    def set_search_after_characters(self, search_after_characters):
        self._search_after_characters = search_after_characters

    @lock
    def set_search_max_results(self, search_max_results):
        self._search_max_results = search_max_results

    @lock
    def set_search_threshold(self, search_threshold):
        self._search_threshold = search_threshold

    @lock
    def set_ignore_filename(self, ignore_filename):
        Ignore.set_ignore_filename(ignore_filename)

    @lock
    def set_paths(self, paths, depths):
        if len(depths) < len(paths):
            raise Exception('depths length does not match paths length')
        if not paths:
            return
        paths, depths = zip(*sorted(zip(paths, depths), key=lambda path_depth: path_depth[0].count(os.sep), reverse=True))
        self._root_paths = paths
        self._depths = depths

    @lock
    def __contains__(self, path):
        paths = set(itertools.chain.from_iterable(self._data.values()))
        return CacheEntry(path, None) in paths

    @property
    @lock
    def paths(self):
        return list(itertools.chain(*self._dirs_d.values(), *self._files_d.values()))

    @property
    @lock
    def search_names(self):
        return list(itertools.chain(self._dirs_d.keys(), self._files_d.keys(), self._files_no_ext_d.keys()))

    @staticmethod
    def _walklevel(directory, level=None):
        num_sep = directory.count(os.sep)
        for root, dirs, files in os.walk(directory):
            num_sep_this = root.count(os.sep)
            if level is not None and level > 0 and num_sep + level <= num_sep_this:
                del dirs[:]
                del files[:]
            yield root, dirs, files

    @staticmethod
    def _get_search_names(path, base_name=True):
        name = path
        if base_name:
            name = os.path.basename(path)
        name_no_ext, ext = os.path.splitext(name)
        search_name_no_ext = Cache.SEARCH_TERM_REGEX.sub('', name_no_ext).lower()
        search_name = search_name_no_ext + ext
        return search_name, search_name_no_ext, ext

    @lock
    def scan(self):
        self._logger.info('Scanning folders')
        now = time()
        
        directories_num = 0
        files_num = 0
        path_dict = {}
        data = {}
        root_matcher = Ignore.get_root_matcher()
        matchers = {}

        for root_path, depth in zip(self._root_paths, self._depths):
            if root_path in data:
                continue
            if not os.path.exists(root_path):
                continue
            if os.path.isfile(root_path):
                search_name, search_name_no_ext, ext = Cache._get_search_names(root_path)
                entry = CacheEntry(root_path, None)
                if search_name not in data:
                    data[search_name] = []
                data[search_name].append(entry)
                path_dict[root_path] = entry
                files_num += 1
                if ext:
                    if search_name_no_ext not in data:
                        data[search_name_no_ext] = []
                    data[search_name_no_ext].append(entry)
                continue
            
            for root_dir, _, file_names in Cache._walklevel(root_path, depth):
                if root_dir in data:
                    continue

                # Get matcher to ignore or not
                parent_matcher = matchers.get(os.path.dirname(root_dir), root_matcher)
                matcher = Ignore.get_matcher(root_dir, file_names, parent_matcher)
                matchers[root_dir] = matcher

                # Check root dir if matches
                root_dir_relpath = os.path.relpath(root_dir, root_path)
                if not matcher(root_dir_relpath.rstrip(os.sep) + os.sep):
                    continue

                directories_num += 1

                root_dir_parent_entry = path_dict.get(root_path)
                if root_dir_parent_entry is None:
                    root_dir_parent_entry = CacheEntry(root_path, None, is_directory=True)
                    root_dir_entry = root_dir_parent_entry
                else:
                    root_dir_entry = CacheEntry(root_dir, root_dir_parent_entry, is_directory=True)

                search_name, _, _ = Cache._get_search_names(root_dir)
                if search_name not in data:
                    data[search_name] = []
                data[search_name].append(root_dir_entry)
                path_dict[root_dir] = root_dir_entry

                for file_name in file_names:
                    file_path = os.path.join(root_dir, file_name)
                    if file_path in path_dict:
                        continue
                    file_relpath = os.path.join(root_dir_relpath, file_name)
                    if not matcher(file_relpath):
                        continue

                    files_num += 1
                    path_dict[file_path] = root_dir_parent_entry
                    entry = CacheEntry(file_path, root_dir_entry)
                    search_name, search_name_no_ext, ext = Cache._get_search_names(file_path)
                    if search_name not in data:
                        data[search_name] = []
                    data[search_name].append(entry)
                    if not ext or ext.lower() not in Cache.COMMON_EXTS:
                        continue
                    if search_name_no_ext not in data:
                        data[search_name_no_ext] = []
                    data[search_name_no_ext].append(entry)

        if data:
            common_prefix = os.path.commonprefix(list(path_dict.keys()))

            path_lengths = map(lambda s: s.count(os.sep), path_dict.keys())
            path_lengths = list(path_lengths)

            shortest_path = min(path_lengths)
            longest_path = max(path_lengths)
        else:
            common_prefix = 0
            shortest_path = 0
            longest_path = 1

        with self._lock:
            self._common_prefix = common_prefix
            self._shortest_path = shortest_path
            self._longest_path = longest_path
            self._data = data
        self._logger.info('Finished scanning in {:.2f}ms found {} directories and {} files'.format(1000 * (time() - now), files_num, directories_num))

    def _get_score(self, search_value, query):
        try:
            search_index = search_value.index(query)
            score = len(query) / len(search_value)
            score_index = (len(query) - search_index) / len(query)
            return score + score_index
        except ValueError:
            return 0

    def _get_path_score(self, entry):
        return 1.36787944117 - math.exp(-1 + entry.relative_path_len / 6)

    @lock
    def search(self, query):
        query = query.strip()
        if not self._search_after_characters <= 0 and len(query) <= self._search_after_characters:
            return []

        matcher = Match(query)
        query, search_value_no_ext, search_value_ext = Cache._get_search_names(query, base_name=False)
        # matches = difflib.get_close_matches(query, values, n=5, cutoff=0.6)

        result_scores = {}
        for search_value in self._data:
            score = matcher(search_value) and 2.0

            if not score:
                score = matcher(search_value, ignorecase=True) and 1.9
            
            if not score:
                score = self._get_score(search_value, query)
                if search_value_ext:
                    score = max(score, self._get_score(search_value, search_value_no_ext))
                if score == 0:
                    continue

            for entry in self._data[search_value]:
                final_score = (score + self._get_path_score(entry)) / 3
                if entry in result_scores:
                    old_score = result_scores[entry]
                    if final_score <= old_score:
                        continue
                result_scores[entry] = final_score

        result_scores = sorted(result_scores.items(), key=lambda item: (item[1], 1 / len(item[0])), reverse=True)
        results = []
        i = 0
        for entry, score in result_scores:
            if score < self._search_threshold  or i >= self._search_max_results:
                break

            result = entry.to_result(score=score)
            results.append(result)
            i += 1

        return results
