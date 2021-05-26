#!/usr/bin/python3

import sys
import os
import pytest

module_path = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(module_path)

from ..parser_logo import Parser
from ..language_errors import ParseError, SyntaxError
from .test_lexer import TextBuffer
from .test_parser import generate_lexer


def test_basic_program():
    TEST_STRINGS = [
        "x=6234",
    ]
    for string in TEST_STRINGS:
        print(f'Generating program: {string}')
        q = generate_lexer(string)
        p = Parser(token_source=q)
        result = p.parse_program()
        print(result)
        print("Executing:")
        result.execute()
        print("Executed")
        print(result.root_context)
