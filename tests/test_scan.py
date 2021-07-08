from os.path import join
from files.cache import Cache
from .utils import SCAN_DIRECTORY, PATHS, DEPTHS, set_cache_settings

def test_scan():
    set_cache_settings('.albertignore2', 2, 0.5, PATHS, DEPTHS)
    Cache().scan()

    assert join(SCAN_DIRECTORY, 'root_file.mp3') in Cache()
    assert join(SCAN_DIRECTORY, '.albertignore2') in Cache()
    assert join(SCAN_DIRECTORY, '.customignore') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads') in Cache()
    assert join(SCAN_DIRECTORY, 'Projects') in Cache()

    assert join(SCAN_DIRECTORY, 'Downloads', '.albertignore2') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'some_file.png') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'some_other_file.pdf') in Cache()
    
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'three_level_dir') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'another_file.zip') in Cache()

    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'three_level_dir', 'three_level_file') in Cache()

    assert join(SCAN_DIRECTORY, 'Projects', 'my_project') in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', '.git') not in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', 'project_file.py') in Cache()

    assert join(SCAN_DIRECTORY, '.hidden_directory') not in Cache()
    assert join(SCAN_DIRECTORY, '.hidden_directory', 'file_in_hidden_directory') not in Cache()

def test_scan_custom_ignore():
    set_cache_settings('.customignore', 2, 0.5, PATHS, DEPTHS)
    Cache().scan()

    assert join(SCAN_DIRECTORY, 'root_file.mp3') in Cache()
    assert join(SCAN_DIRECTORY, '.albertignore2') not in Cache()
    assert join(SCAN_DIRECTORY, '.customignore') not in Cache()

    assert join(SCAN_DIRECTORY, 'Downloads') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', '.albertignore2') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', '.customignore') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'some_file.png') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'some_other_file.pdf') not in Cache()
    
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'three_level_dir') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'another_file.zip') not in Cache()

    assert join(SCAN_DIRECTORY, 'Projects', 'my_project') in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', '.git') in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', 'project_file.py') in Cache()

    assert join(SCAN_DIRECTORY, '.hidden_directory') in Cache()
    assert join(SCAN_DIRECTORY, '.hidden_directory', 'file_in_hidden_directory') in Cache()

def test_scan_depth_1():
    set_cache_settings(None, 2, 0.5, PATHS, [1])
    Cache().scan()

    assert join(SCAN_DIRECTORY, 'Downloads') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', '.albertignore2') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'some_file.png') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'some_other_file.pdf') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'three_level_dir') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'another_file.zip') not in Cache()

    assert join(SCAN_DIRECTORY, 'Projects', 'my_project') not in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', '.git') not in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', 'project_file.py') not in Cache()

def test_scan_depth_2():
    set_cache_settings(None, 2, 0.5, PATHS, [2])
    Cache().scan()

    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'another_file.zip') not in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'three_level_dir') not in Cache()

    assert join(SCAN_DIRECTORY, 'Projects', 'my_project') in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', '.git') not in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', 'project_file.py') not in Cache()

def test_scan_depth_3():
    set_cache_settings(None, 2, 0.5, PATHS, [3])
    Cache().scan()

    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'another_file.zip') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'three_level_dir') in Cache()
    assert join(SCAN_DIRECTORY, 'Downloads', 'two_level_dir', 'three_level_dir', 'three_level_file') not in Cache()

    assert join(SCAN_DIRECTORY, 'Projects', 'my_project') in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', '.git') in Cache()
    assert join(SCAN_DIRECTORY, 'Projects', 'my_project', 'project_file.py') in Cache()
