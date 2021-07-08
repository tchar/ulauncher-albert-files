# -*- coding: utf-8 -*-
'''Converter for currency, units and calculator.

Current backends: fixer.io.

Synopsis: "10 dollars to eur, cad" "10 meters to inches" "10 + sqrt(2)" "cos(pi + 3i)"'''

# Uncomment below to set keyword to files (leave a space after keyword)
__triggers__ = '?'
__title__ = 'Files'
__version__ = '0.0.1'
__authors__ = 'Tilemachos Charalampous'
__exec_deps__ = ['xdg-open']
__py_deps__	= ['pathspec']


TRIGGERS = globals().get('__triggers__') or []
import os
import sys
MAIN_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(MAIN_DIR)
from files.launcher import Launcher
Launcher.set('albert')
from files.service import FilesService
from files.icon import IconRegistry
from albert import ProcAction, Item

home = os.path.expanduser('~')
replace_home = lambda path: path.replace(home, '~', 1)

def initialize():
    FilesService().load_settings_albert(os.path.join(MAIN_DIR, 'settings.ini'))
    FilesService().run()

def finalize():
    FilesService.stop()

def handleQuery(query):
    if TRIGGERS and not query.isTriggered:
        return
    query_str = query.string
    if not query_str:
        return
    query.disableSort()
    results = FilesService().search(query_str)
    items = []

    for result in results:
        name = result.name
        path = result.path
        
        icon = IconRegistry().get_icon(result)
        text = name
        subtext = replace_home(path)
        actions = [
            ProcAction(
                text='Open {}'.format(path),
                commandline=['xdg-open', path],
            ),
        ]
        items.append(Item(
            id=__title__,
            icon=icon,
            text=text,
            subtext=subtext,
            actions=actions
        ))
    if not items:
        return None
    return items
