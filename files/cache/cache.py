import os
from queue import Queue
from re import search
from time import time
import math
import itertools
from threading import RLock
from .search_results import SearchResults
from .entry import CacheEntry
from .. import logging
from ..match import Ignore, Match
from ..utils import Singleton, lock


class Cache(metaclass=Singleton):
    # SEARCH_TERM_REGEX = re.compile(r'([_\-])', flags=re.IGNORECASE)
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
        self._entries = {}
        self._common_prefix = ''
        self._shortest_path = 0
        self._longest_path = 1
        self._lock = RLock()
        self._logger = logging.getLogger(__name__)
        self._search_results = SearchResults()

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
        paths_dict = {}
        root_matcher = Ignore.get_root_matcher()
        matchers = {}

        for root_path, depth in zip(self._root_paths, self._depths):
            if root_path in paths_dict:
                continue
            if not os.path.exists(root_path):
                continue
            if os.path.isfile(root_path):
                entry = CacheEntry(root_path, None)
                paths_dict[root_path] = entry
                files_num += 1
                continue
            
            for root_dir, _, file_names in Cache._walklevel(root_path, depth):
                if root_dir in paths_dict:
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

                root_dir_parent_entry = paths_dict.get(root_path)
                if root_dir_parent_entry is None:
                    root_dir_parent_entry = CacheEntry(root_path, None, is_directory=True)
                    root_dir_entry = root_dir_parent_entry
                else:
                    root_dir_entry = CacheEntry(root_dir, root_dir_parent_entry, is_directory=True)

                paths_dict[root_dir] = root_dir_entry

                for file_name in file_names:
                    file_path = os.path.join(root_dir, file_name)
                    if file_path in paths_dict:
                        continue
                    file_relpath = os.path.join(root_dir_relpath, file_name)
                    if not matcher(file_relpath):
                        continue

                    files_num += 1
                    entry = CacheEntry(file_path, paths_dict[root_path])
                    paths_dict[file_path] = entry

        self._search_results.clear()
        self._entries = set(paths_dict.values())
        self._logger.info('Finished scanning in {:.2f}ms found {} directories and {} files'.format(1000 * (time() - now), files_num, directories_num))

    def _get_score(self, entry_attr, query, relpath=False):
        try:
            index = entry_attr.index(query)
            if relpath:
                entry_end = entry_attr[index + len(query):]
                if '/' in entry_end: return 0

            score = len(query) / len(entry_attr)
            score_index = (len(query) - index) / len(query)
            return score + score_index
        except ValueError:
            return 0

    def _get_path_score(self, entry):
        return 1.36787944117 - math.exp(-1 + entry.relpath_len / 6)

    @lock
    def search(self, query):
        query = query.strip()
        original_query = query
        if not self._search_after_characters <= 0 and len(query) <= self._search_after_characters:
            return []

        prev_results = self._search_results.get_results(original_query)
        if prev_results is not None:
            self._logger.info('Returning previous results')
            return prev_results

        prev_entries = self._search_results.get_entries(original_query)
        if prev_entries is not None:
            self._logger.info('Searching from previous entries')
            entries_to_search = prev_entries
        else:
            entries_to_search = self._entries

        # Search previous results
        query = query.lower()
        query, query_ext = os.path.splitext(query)
        if query_ext:
            query = query + query_ext
        if query.endswith('/'):
            query = query[:-1]

        matcher = Match(query)

        result_scores = {}
        for entry in entries_to_search:
            score = (
                # (matcher(entry.relpath) and 2.0) or
                (matcher(entry.relpath, ignorecase=True) and 2.0) or
                # (matcher(entry.name) and 1.9) or 
                (matcher(entry.name, ignorecase=True) and 1.95)
            )

            if not score:
                if query_ext:
                    relpath = entry.relpath_lower
                    name = entry.name_lower
                else:
                    relpath = entry.relpath_basename_lower
                    name = entry.basename_lower
                
                score = (
                    self._get_score(relpath, query, relpath=True),
                    self._get_score(name, query, relpath=False)
                )
                score = max(score)

            if not score:
                continue
            
            final_score = (score + self._get_path_score(entry)) / 3
            result_scores[entry] = final_score

        self._search_results.add_entries(original_query, list(result_scores.keys()))

        result_scores = sorted(result_scores.items(), key=lambda item: (item[1], 1 / (item[0].relpath_len + 1)), reverse=True)
        results = []
        i = 0
        for entry, score in result_scores:
            if score < self._search_threshold  or i >= self._search_max_results:
                break

            result = entry.to_result(score=score)
            results.append(result)
            i += 1

        self._search_results.add_results(original_query, results)
        return results
