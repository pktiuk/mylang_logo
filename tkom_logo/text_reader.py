from abc import ABC, abstractmethod

from .shared import Location


class TextReader(ABC):
    """Base class for queque reading letters
    """
    @abstractmethod
    def get_char(self) -> str:
        """if buffer empty then wait

        Returns:
            single character (or 0x00 when closing)
        """
        raise NotImplementedError

    def close(self):
        """Prepares Reader for closing
        get_char will return 0x00 instead of waiting for
        empty queue
        """
        pass

    @abstractmethod
    def get_location(self) -> Location:
        raise NotImplementedError


class StringReader(TextReader):
    def __init__(self, msg: str):
        self.msg = msg
        self.counter = 0
        self.lineno = 0
        self.charnr = -1
        self.newline = False

    def get_char(self):
        self.counter += 1
        self.charnr += 1
        if self.counter <= len(self.msg):
            if self.newline:
                self.lineno += 1
                self.charnr = 0
                self.newline = False

            if self.msg[self.counter - 1] == "\n":
                self.newline = True
            return self.msg[self.counter - 1]
        else:
            return '\0'

    def get_location(self) -> Location:
        return Location(self.lineno, self.charnr)


class FileReader(StringReader):
    def __init__(self, filename: str):
        file = open(filename)
        msg = file.read()
        file.close()
        super().__init__(msg)
