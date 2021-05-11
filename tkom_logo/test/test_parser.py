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
from lexer import Lexer


def generate_queue(text) -> Queue:
    buf = TextBuffer(text)
    lexer = Lexer(buf)
    tokens = []
    for i in range(90):
        tokens.append(lexer.get_token())

    q = Queue()
    for token in tokens:
        q.put(token)
    return q


def test_parser_stability():
    q = generate_queue("(-33*1)/-2")
    p = Parser(token_source=q)
    result = p.parse()
    print(result)
    q = generate_queue("2+3*4")
    p = Parser(token_source=q)
    result = p.parse()
    print(result)
    q = generate_queue("23==3&& 5>2")
    p = Parser(token_source=q)
    result = p.parse()
    print(result)


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
    assert result.token.value == "*"
    assert result.children[1].token == tokens[-2]