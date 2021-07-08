class Launcher:
    launcher = None

    @classmethod
    def set(cls, value):
        cls.launcher = value

    @classmethod
    def get(cls):
        return cls.launcher