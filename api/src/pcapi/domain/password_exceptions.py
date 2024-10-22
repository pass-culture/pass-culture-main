class WeakPassword(Exception):
    def __init__(self, errors: dict):
        self.errors = errors
