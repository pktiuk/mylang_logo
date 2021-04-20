import sys
import os
import pytest

module_path = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(module_path)

from tkom_logo.lexer import Lexer, TextBuffer


class TextBuffer:
    def __init__(self, msg: str):
        self.msg = msg
        self.counter = 0
        self.lineno = 0

    def get_char(self):
        self.counter += 1
        if self.counter <= len(self.msg):
            return self.msg[self.counter - 1]
        else:
            return "+"


class TestLexer:
    def test_base(self):
        t = TextBuffer("<=(\"ukafsd\"+312.543/1322())")
        lexer = Lexer(source=t)
        assert lexer.get_token().value == "<="
