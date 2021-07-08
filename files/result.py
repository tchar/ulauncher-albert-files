import os

class Result:
    def __init__(self, path, is_directory, score):
        self.path = path
        self.is_directory = is_directory
        self.score = score

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def ext(self):
        _, ext = os.path.splitext(self.path)
        return ext or None

    def __str__(self):
        directory_str = 'd ' if self.is_directory else '' 
        return '{}={}{}: {}'.format(self.score, directory_str, self.name, self.path)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.path)