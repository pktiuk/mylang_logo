#!/usr/bin/python3

import sys
import os
import pytest

module_path = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(module_path)

from ..parser_logo import Parser
from ..language_errors import ParseError, SyntaxError
from ..context import Context, RootContext
from .test_lexer import TextBuffer
from .test_parser import generate_lexer


def check_context(context: Context, expected_values: dict):
    for key, value in expected_values.items():
        assert context.get_element(key) == value


def test_basic_program_with_context():
    TEST_STRINGS = [
        "x=6234", "x=12 y=34 z=x", "x=21+9", "x=43/32 y=3*2", "x=43>32",
        "x=43<4 && 33<2", "x=32>43-32||3"
    ]
    TEST_VALUES = [{
        "x": 6234
    }, {
        "x": 12,
        "y": 34,
        "z": 12
    }, {
        "x": 30
    }, {
        "x": 43 / 32,
        "y": 6
    }, {
        "x": True
    }, {
        "x": False
    }, {
        "x": True
    }]
    for string, values in zip(TEST_STRINGS, TEST_VALUES):
        print(f'Generating program: {string}')
        q = generate_lexer(string)
        p = Parser(token_source=q)
        result = p.parse_program()
        print(result)
        print("Executing:")
        result.execute()
        print("Executed")
        print(result.root_context)
        check_context(result.root_context, values)


def test_block_constructions():
    TEST_TUPLES = [("""x = 0
        y=0
        while(x==0)
        {
            y=y+1
            x=1
        }""", {
        "x": 1,
        "y": 1
    })]

    for string, values in TEST_TUPLES:
        print(f'Generating program: {string}')
        q = generate_lexer(string)
        p = Parser(token_source=q)
        result = p.parse_program()
        print(result)
        print("Executing:")
        result.execute()
        print("Executed")
        print(result.root_context)
        check_context(result.root_context, values)


def test_context():
    root = RootContext()
    root.define_element("x", 0)
    child = Context(parent_context=root)
    child.define_element("x", 1)
    print(root)
    print(child)
    assert child.get_element("x") == root.get_element("x")
