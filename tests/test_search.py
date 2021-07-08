from os.path import join
from files.cache import Cache
from .utils import SCAN_DIRECTORY, PATHS, DEPTHS, set_cache_settings

def test_search():
    set_cache_settings(None, 2, 0.5, PATHS, DEPTHS)
    Cache().scan()

    results = Cache().search('some')
    assert len(results) == 2
    assert results[0].path == join(SCAN_DIRECTORY, 'Downloads', 'some_file.png')
    assert results[0].is_directory == False
    assert results[1].path == join(SCAN_DIRECTORY, 'Downloads', 'some_other_file.pdf')
    assert results[1].is_directory == False

    results = Cache().search('file_in')
    assert len(results) == 1
    assert results[0].path == join(SCAN_DIRECTORY, '.hidden_directory', 'file_in_hidden_directory')
    assert results[0].is_directory == False

    results = Cache().search('_level_dir')
    assert len(results) == 2
    assert results[0].path == join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir')
    assert results[0].is_directory == True
    assert results[1].path == join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'three_level_dir')
    assert results[1].is_directory == True
