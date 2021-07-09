class Launcher:
    ALBERT = 0
    ULAUNCHER = 1
    _launcher = None

    @classmethod
    def set(cls, value):
        value = str(value).lower()
        if value in set(['albert', 'albertlauncher']):
            cls._launcher = cls.ALBERT
        elif value in set(['ulauncher']):
            cls._launcher = cls.ULAUNCHER

    @classmethod
    def get(cls):
        return cls._launcher
