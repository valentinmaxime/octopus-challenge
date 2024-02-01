""" Exception classes """
class ConfigError(Exception):
    """ Config exception class."""
    def __init__(self, message="A config error occurred"):
        self.message = message
        super().__init__(self.message)

class DataError(Exception):
    """ Header Data exception class."""
    def __init__(self, message="A data error occurred"):
        self.message = message
        super().__init__(self.message)

class FileError(Exception):
    """ Header Data exception class."""
    def __init__(self, message="An file error occurred"):
        self.message = message
        super().__init__(self.message)
