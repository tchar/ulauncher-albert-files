import os
from time import time
from configparser import ConfigParser, MissingSectionHeaderError
from threading import RLock, Timer
from . import logging
from .launcher import Launcher
from .icon import IconRegistry
from .cache import Cache
from .utils import lock, type_or_default, Singleton

class FilesService(metaclass=Singleton):
    def __init__(self):
        self._scan_every_minutes = 15
        self._lock = RLock()
        self._running = False
        self._logger = logging.getLogger(__name__)

    @lock
    def _run_thread(self):
        if self._scan_every_minutes <= 0 or not self._running:
            self._running = False
            return
        Cache().scan()
        thread = Timer(self._scan_every_minutes * 60.0, self._run_thread)
        thread.setDaemon(True)
        thread.start()

    @lock
    def search(self, search_value):
        return Cache().search(search_value)

    @lock
    def run(self):
        if self._running:
            return
        self._running = True
        thread = Timer(0.0, self._run_thread)
        thread.setDaemon(True)
        thread.run()

    @lock
    def stop(self):
        self._running = False
    
    @lock
    def set_scan_every_minutes(self, scan_every_minutes, _set=True):
        scan_every_minutes = type_or_default(scan_every_minutes, float, 15)
        if _set:
            self._scan_every_minutes = scan_every_minutes
        return scan_every_minutes

    @lock
    def set_directories(self, directories, _set=True):
        paths = []
        depths = []
        for path in directories.splitlines():
            path = path.strip()
            path = path.rsplit('=', 1)
            if len(path) == 2:
                path, depth = path
                depth = depth.strip()
            else:
                path, depth = path[0], 0
            path = path.strip()
            path = os.path.expanduser(path)
            path = os.path.abspath(path)
            paths.append(path)

            depth = type_or_default(depth, int, 0)
            depths.append(depth)
        if _set:
            Cache().set_paths(paths, depths)
        return paths, depths

    @lock
    def set_search_after_characters(self, search_after_characters, _set=True):
        search_after_characters = type_or_default(search_after_characters, int, 2)
        if _set:
            Cache().set_search_after_characters(search_after_characters)
        return search_after_characters
        
    @lock
    def set_search_max_results(self, search_max_results, _set=True):
        search_max_results = type_or_default(search_max_results, int, 5)
        if _set:
            Cache().set_search_max_results(search_max_results)
        return search_max_results
        

    @lock
    def set_search_threshold(self, search_threshold, _set=True):
        search_threshold = type_or_default(search_threshold, int, 0.5)
        if _set:
            Cache().set_search_threshold(search_threshold)
        return search_threshold

    @lock
    def set_ignore_filename(self, ignore_filename, _set=True):
        fallback = '.ulauncherignore' if Launcher.get() == 'ulauncher' else '.albertignore2'
        ignore_filename = ignore_filename.strip() or fallback
        if _set:
            Cache().set_ignore_filename(ignore_filename)
        return ignore_filename

    
    @lock
    def set_icon_theme(self, icon_theme, _set=True):
        icon_theme = icon_theme.strip() or 'square-o'
        if _set:
            IconRegistry().set_icon_pack(icon_theme)
        return icon_theme

    @lock
    def set_use_built_in_folder_theme(self, use_built_in_folder_theme, _set=True):
        print(use_built_in_folder_theme)
        use_built_in_folder_theme = use_built_in_folder_theme.strip() or 'false'
        use_built_in_folder_theme = use_built_in_folder_theme.lower() == 'true'
        if _set:
            IconRegistry().set_use_built_in_folder_theme(use_built_in_folder_theme)
        return use_built_in_folder_theme
        

    @lock
    def load_settings_ulauncher(self, scan_every_minutes, directories,
                                search_after_characters, search_max_results,
                                search_threshold, ignore_filename, icon_theme,
                                use_built_in_folder_theme):
        
        self._logger.info('Loading settings')
        now = time()
        scan_every_minutes = self.set_scan_every_minutes(scan_every_minutes, _set=False)
        search_after_characters = self.set_search_after_characters(search_after_characters, _set=False)
        search_max_results = self.set_search_max_results(search_max_results, _set=False)
        search_threshold = self.set_search_threshold(search_threshold, _set=False)
        ignore_filename = self.set_ignore_filename(ignore_filename, _set=False)
        paths, depths = self.set_directories(directories, _set=False)
        icon_theme = self.set_icon_theme(icon_theme, _set=False)
        use_built_in_folder_theme = self.set_use_built_in_folder_theme(use_built_in_folder_theme, _set=False)

        self._scan_every_minutes = scan_every_minutes
        time_elapsed = 1000 * (time() - now)
        self._logger.info(
            'Loaded Settings in {:.2f}ms:'
            '\n\tScan Every Minutes = {}'
            '\n\tSearch After Characters = {}'
            '\n\tSearch Maximum Results = {}'
            '\n\tSearch Threshold = {}'
            '\n\tIgnore Filename = {}'
            '\n\tIcon theme = {}'
            '\n\tUse built in folder theme = {}'
            '\n\tDirectories = {}'.format(
                time_elapsed, scan_every_minutes, search_after_characters, search_max_results,
                search_threshold, ignore_filename, icon_theme, use_built_in_folder_theme, paths
            )
        )
        Cache().set_search_after_characters(search_after_characters)
        Cache().set_search_max_results(search_max_results)
        Cache().set_search_threshold(search_threshold)
        Cache().set_ignore_filename(ignore_filename)
        Cache().set_paths(paths, depths)
        IconRegistry().set_icon_pack(icon_theme)
        IconRegistry().set_use_built_in_folder_theme(use_built_in_folder_theme)
        
    @lock
    def load_settings_albert(self, file_path):
        self._logger.info('Loading settings')
        now = time()
        if not os.path.isfile(file_path):
            self._logger.warning('Settings file path is not a file, falling back to default settings: {}'.format(file_path))
        config = ConfigParser(allow_no_value=True)
        try:
            config.read(file_path)
        except MissingSectionHeaderError as e:
            self._logger.warning('Missing section DEFAULT, falling back to default settings: {}'.format(e))

        default = config['DEFAULT']

        scan_every_minutes = default.get('SCAN_EVERY_MINUTES')
        scan_every_minutes = self.set_scan_every_minutes(scan_every_minutes, _set=False)

        search_after_characters = default.get('SEARCH_AFTER_CHARACTERS')
        search_after_characters = self.set_search_after_characters(search_after_characters, _set=False)

        search_max_results = default.get('SEARCH_MAX_RESULTS')
        search_max_results = self.set_search_max_results(search_max_results, _set=False)

        search_threshold = default.get('SEARCH_THRESHOLD', Cache()._search_threshold)
        search_threshold = self.set_search_threshold(search_threshold, _set=False)

        ignore_filename = default.get('IGNORE_FILENAME')
        ignore_filename = self.set_ignore_filename(ignore_filename, _set=False)

        icon_theme = default.get('ICON_THEME')
        icon_theme = self.set_icon_theme(icon_theme, _set=False)

        use_built_in_folder_theme = default.get('USE_BUILT_IN_FOLDER_THEME')
        use_built_in_folder_theme = self.set_use_built_in_folder_theme(use_built_in_folder_theme, _set=False)

        paths = []
        depths = []
        for section in config.sections():
            if not section.strip().startswith('DIRECTORY'):
                continue
            path = config[section].get('PATH', '').strip()
            path = os.path.expanduser(path)
            path = os.path.abspath(path)
            depth = config[section].get('DEPTH', 0.0)
            depth = type_or_default(depth, float, 0.0)
            paths.append(path)
            depths.append(depth)
        
        self._scan_every_minutes = scan_every_minutes
        time_elapsed = 1000 * (time() - now)
        self._logger.info(
            'Loaded Settings in {:.2f}ms:'
            '\n\tSCAN_EVERY_MINUTES={}'
            '\n\tSEARCH_AFTER_CHARACTERS={}'
            '\n\tSEARCH_MAX_RESULTS={}'
            '\n\tSEARCH_THRESHOLD={}'
            '\n\tIGNORE_FILENAME={}'
            '\n\tICON_THEME={}'
            '\n\tUSE_BUILT_IN_ICON_THEME={}'
            '\n\DIRECTORIES={}'.format(
                time_elapsed, scan_every_minutes, search_after_characters, search_max_results,
                search_threshold, ignore_filename, icon_theme, use_built_in_folder_theme, paths
            )
        )
        Cache().set_search_after_characters(search_after_characters)
        Cache().set_search_max_results(search_max_results)
        Cache().set_search_threshold(search_threshold)
        Cache().set_ignore_filename(ignore_filename)
        Cache().set_paths(paths, depths)
        IconRegistry().set_icon_pack(icon_theme)
        IconRegistry().set_use_built_in_folder_theme(use_built_in_folder_theme)
