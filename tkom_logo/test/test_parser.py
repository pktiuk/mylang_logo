#!/usr/bin/python3

import sys
import os
import pytest
from queue import Queue

module_path = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(module_path)

from shared import Token, TokenType, Location
from parser_logo import Parser
from language_errors import UnexpectedCharacterError, ParseError
from test_lexer import TextBuffer


def test_parser():
    assert True


def test_multiplications():
    tokens = [
        Token(TokenType.CONST, 22),
        Token(TokenType.MULT_OPERATOR, "*"),
        Token(TokenType.CONST, 4),
        Token(TokenType.MULT_OPERATOR, "/"),
        Token(TokenType.CONST, 3),
        Token(TokenType.MULT_OPERATOR, "*"),
        Token(TokenType.CONST, 1),
        Token(TokenType.EOL, "\n")
    ]
    q = Queue()
    for token in tokens:
        q.put(token)
    p = Parser(token_source=q)
    result = p.parse()
    print(result)
