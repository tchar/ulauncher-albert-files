import logging
from .launcher import Launcher
try:
    from albert import debug, info, warning, critical
except ImportError:
    debug = print
    info = print
    warning = print
    critical = print

class AlbertLogger:
    def __init__(self, name):
        self._name = name

    @staticmethod
    def _escape(message):
        return message.replace('%', '\\%')

    def _log(self, func, message, *args):
        message = str(message)
        message = AlbertLogger._escape(message)
        if args:
            message = message % args
        message = '{}: {}'.format(self._name, message)
        func(message)

    def debug(self, message, *args):
        self._log(debug, message, *args)

    def info(self, message, *args):
        self._log(info, message, *args)

    def warning(self, message, *args):
        self._log(warning, message, *args)

    def error(self, message, *args):
        self._log(critical, message, *args)
    
def getLogger(name):
    if Launcher.get() == 'albert':
        return AlbertLogger(name)
    return logging.getLogger(name)