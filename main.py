from files.launcher import Launcher
Launcher.set('ulauncher')
import os
from files.service import FilesService
from files.icon import IconRegistry
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent, SystemExitEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction

home = os.path.expanduser('~')
replace_home = lambda path: path.replace(home, '~', 1)

class FilesExtension(Extension):
    def __init__(self):
        super(FilesExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        self.subscribe(SystemExitEvent, SystemExitEventListener)

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query_str = event.get_argument() or ''
        results = FilesService().search(query_str)
        
        items = []
        for result in results:
            icon = IconRegistry().get_icon(result)
            name = result.name
            path = result.path
            on_enter = OpenAction(path)
        
            items.append(ExtensionResultItem(
                icon=icon,
                name=name,
                description=replace_home(path),
                highlightable=True,
                on_enter=on_enter
            ))
        
        return RenderResultListAction(items)

class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        super().on_event(event, extension)

        scan_every_minutes = event.preferences['scan_every_minutes']
        directories = event.preferences['directories']
        search_after_characters = event.preferences['search_after_characters']
        search_max_results = event.preferences['search_max_results']
        search_threshold = event.preferences['search_threshold']
        ignore_filename = event.preferences['ignore_filename']
        icon_theme = event.preferences['icon_theme'] 
        use_built_in_folder_theme = event.preferences['use_built_in_folder_theme']

        FilesService().load_settings_ulauncher(scan_every_minutes, directories, 
                                               search_after_characters, search_max_results,
                                               search_threshold, ignore_filename,
                                               icon_theme, use_built_in_folder_theme)
        FilesService().run()

class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        super().on_event(event, extension)

        service = FilesService()
        if event.id == 'scan_every_minutes':
            service.set_scan_every_minutes(event.new_value)
        elif event.id == 'directories':
            service.set_directories(event.new_value)
        elif event.id == 'search_after_characters':
            service.set_search_after_characters(event.new_value)
        elif event.id == 'search_max_results':
            service.set_search_max_results(event.new_value)
        elif event.id == 'search_threshold':
            service.set_search_threshold(event.new_value)
        elif event.id == 'ignore_filename':
            service.set_ignore_filename(event.new_value)
        elif event.id == 'icon_theme':
            service.set_icon_theme(event.new_value)
        elif event.id == 'use_built_in_folder_theme':
            service.set_use_built_in_folder_theme(event.new_value)

class SystemExitEventListener(EventListener):
    def on_event(event, extension):
        FilesService().stop()

if __name__ == '__main__':
    FilesExtension().run()