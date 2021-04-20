class Logger(object):
    def __init__(self, *args):
        super(Logger, self).__init__(*args)

    def info(self, msg):
        raise NotImplementedError

    def warn(self, msg):
        raise NotImplementedError

    def error(self, msg):
        raise NotImplementedError

    def log(self, msg):
        raise NotImplementedError


class ConsoleLogger(Logger):
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'

    def __init__(self, *args):
        super(ConsoleLogger, self).__init__(*args)

    def info(self, msg):
        print(self.GREEN + msg + self.ENDC)

    def warn(self, msg):
        print(self.WARNING + msg + self.ENDC)

    def error(self, msg):
        print(self.ERROR + msg + self.ENDC)

    def log(self, msg):
        print(msg)
