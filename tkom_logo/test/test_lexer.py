#!/usr/bin/python3

import sys
import os
import pytest

module_path = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(module_path)

from shared import Token, TokenType, Location
from lexer import Lexer, UnexpectedCharacterError, ParseError, TextReader


class TextBuffer(TextReader):
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
            return "\x00"

    def get_location(self) -> Location:
        return Location(self.lineno, self.charnr)

    def close(self):
        pass


def test_lexer():
    t = TextBuffer("""<=(\"word\"+         312.543/1322(

    ))""")
    lexer = Lexer(source=t)
    assert lexer.get_token() == Token(TokenType.COMP_OPERATOR, "<=",
                                      Location(0, 0))
    assert lexer.get_token() == Token(TokenType.OPEN_PAREN, "(",
                                      Location(0, 2))
    assert lexer.get_token() == Token(TokenType.CONST, '"word"',
                                      Location(0, 3))
    assert lexer.get_token() == Token(TokenType.ADD_OPERATOR, "+",
                                      Location(0, 9))
    assert lexer.get_token() == Token(TokenType.CONST, "312.543",
                                      Location(0, 19))
    assert lexer.get_token() == Token(TokenType.MULT_OPERATOR, "/",
                                      Location(0, 26))
    assert lexer.get_token() == Token(TokenType.CONST, "1322", Location(0, 27))
    assert lexer.get_token() == Token(TokenType.OPEN_PAREN, "(",
                                      Location(0, 31))
    assert lexer.get_token() == Token(TokenType.EOL, "\n", Location(0, 32))
    assert lexer.get_token() == Token(TokenType.EOL, "\n", Location(1, 0))
    assert lexer.get_token() == Token(TokenType.CLOSE_PAREN, ")",
                                      Location(2, 4))
    assert lexer.get_token() == Token(TokenType.CLOSE_PAREN, ")",
                                      Location(2, 5))


def test_lexer2():
    t = TextBuffer("""n=432+32""")
    lexer = Lexer(source=t)
    assert lexer.get_token() == Token(TokenType.IDENTIFIER, "n",
                                      Location(0, 0))
    assert lexer.get_token() == Token(TokenType.ASSIGNMENT_OPERATOR, "=",
                                      Location(0, 1))
    assert lexer.get_token() == Token(TokenType.CONST, "432", Location(0, 2))
    assert lexer.get_token() == Token(TokenType.ADD_OPERATOR, "+",
                                      Location(0, 5))
    assert lexer.get_token() == Token(TokenType.CONST, "32", Location(0, 6))


def test_wrong_identifiers():
    s = TextBuffer("1ls")
    lexer = Lexer(source=s)
    with pytest.raises(UnexpectedCharacterError):
        print(lexer.get_token())

    s = TextBuffer("1312.43ls")
    lexer = Lexer(source=s)
    with pytest.raises(UnexpectedCharacterError):
        print(lexer.get_token())

    s = TextBuffer("1312.")
    lexer = Lexer(source=s)
    with pytest.raises(ParseError):
        print(lexer.get_token())
