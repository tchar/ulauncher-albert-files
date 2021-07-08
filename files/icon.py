import os
import re
from .launcher import Launcher
from .utils import Singleton

if Launcher.get() == 'albert':
    try:
        from albert import iconLookup as iconLookup
    except ImportError:
        iconLookup = lambda _: None
else:
    try:
        from gi.repository import Gtk
        icon_theme = Gtk.IconTheme.get_default()
        def iconLookup(icon_name):
            icon = icon_theme.lookup_icon(icon_name, 48, 0)
            if icon:
                return icon.get_filename()
            return None
    except ImportError:
        iconLookup = lambda _: None


class IconRegistry(metaclass=Singleton):
    ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    FOLDER_ICONS_REGEX = re.compile(
        r'^\s*'
        r'(?P<folder_copy_cloud>copy(\-|_|\s*|)cloud)|'
        r'(?P<folder_documents>documents)|'
        r'(?P<folder_download>downloads?)|'
        r'(?P<folder_dropbox>drop\s?box)|'
        r'(?P<folder_favorites>favorites)|'
        r'(?P<folder_games>games?)|'
        r'(?P<folder_git>git?)|'
        r'(?P<folder_google_drive>google(\-|_|\s*|)drive?)|'
        r'(?P<folder_image_people>(people|contacts))|'
        r'(?P<folder_important>(important|urgent))|'
        r'(?P<folder_java>java)|'
        r'(?P<folder_locked>lock(ed)?)|'
        r'(?P<folder_unlocked>unlock(ed)?)|'
        r'(?P<folder_mail>(e\-)?mail)|'
        r'(?P<folder_mailcloud>mail(\-|_|\s*|)cloud)|'
        r'(?P<folder_mega>mega((\.co)?\.nz)?)|'
        r'(?P<folder_meocloud>meo(\-|_|\s*|)cloud)|'
        r'(?P<folder_music>(music|songs?))|'
        r'(?P<folder_owncloud>own(\-|_|\s*|)cloud)|'
        r'(?P<folder_pcloud>p(\-|_|\s*|)cloud)|'
        r'(?P<folder_photo>(photo|picture)s?)|'
        r'(?P<folder_print>print(er)?s?)|'
        r'(?P<folder_private>private)|'
        r'(?P<folder_publicshare>(public|shared?))|'
        r'(?P<folder_recent>recents?)|'
        r'(?P<folder_remote>remotes?)|'
        r'(?P<folder_script>scripts?)|'
        r'(?P<folder_steam>steam?)|'
        r'(?P<folder_templates>templates?)|'
        r'(?P<folder_torrent>torrents?)|'
        r'(?P<folder_vbox>v(irtual)(\-|_|\s*|)box?)|'
        r'(?P<folder_video>video(s|(\-|_|\s*|)clips?)?)|'
        r'(?P<folder_wine>win(e|dows(\-|_|\s*|)emu(lators?)?))|'
        r'(?P<folder_yandex_disk>yandex)|'
        r'(?P<folder_desktop>desktops?)|'
        r'(?P<folder_home>homes?)|'
        r'(?P<user_trash>(trash|bin)?)'
        r'\s*$', flags=re.IGNORECASE)

    def __init__(self):
        self._icon_pack = None
        self._icons = {}
        self._learned_folders = {}

    def get_icon(self, result):
        default = self._icons.get('default')
        if not result.is_directory:
            if not result.ext:
                return default
            return self._icons.get(result.ext[1:], default)
        
        result_name = result.name
        result_name_lower = result_name.lower()

        if self._use_built_in_folder_theme:
            return self._icons.get('folder', default)

        icon = self._learned_folders.get(result_name_lower)
        if icon:
            return icon

        icon_name_match = IconRegistry.FOLDER_ICONS_REGEX.match(result_name_lower)
        if icon_name_match:
            icon_name_dict = icon_name_match.groupdict()
            for key, value in icon_name_dict.items():
                if value is None:
                    continue
                icon = iconLookup(key.replace('_', '-'))
                break

        icon = icon or iconLookup('folder') or self._icons.get('folder', default)
        self._learned_folders[result_name_lower] = icon
        return icon

    @staticmethod
    def _get_icons(icon_pack_path):
        icons = {}
        exts = set({'.svg', '.png', '.jpg', '.jpeg', '.ico'})
        for icon_file_name in os.listdir(icon_pack_path):
            icon_path = os.path.join(icon_pack_path, icon_file_name)
            icon_name, icon_ext = os.path.splitext(icon_file_name)
            if icon_ext not in exts:
                continue
            icons[icon_name] = icon_path
        return icons

    def set_icon_pack(self, icon_pack):
        icon_pack_path = os.path.join(IconRegistry.ICON_DIR, 'images', icon_pack)
        if not os.path.isdir(icon_pack_path):
            self._icon_pack = None
            return
        icons = IconRegistry._get_icons(icon_pack_path)
        directories_icon_pack_path = os.path.join(IconRegistry.ICON_DIR, 'images', 'extra')
        if os.path.isdir(directories_icon_pack_path):
            icons = {**icons, **IconRegistry._get_icons(directories_icon_pack_path)}
        self._icons = icons

    def set_use_built_in_folder_theme(self, use_built_in_folder_theme):
        self._use_built_in_folder_theme = use_built_in_folder_theme