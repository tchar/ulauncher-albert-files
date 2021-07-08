import os
from files.cache import Cache

ROOT_DIR = os.path.realpath(os.path.dirname(__file__))
SCAN_DIRECTORY = os.path.join(ROOT_DIR, 'template_structure')
PATHS = [SCAN_DIRECTORY]
DEPTHS = [0]

def set_cache_settings(ignore_filename, search_after_characters, search_threshold, paths, depths):
    Cache().set_ignore_filename(ignore_filename)
    Cache().set_search_after_characters(search_after_characters)
    Cache().set_search_threshold(search_threshold)
    Cache().set_paths(paths, depths)
