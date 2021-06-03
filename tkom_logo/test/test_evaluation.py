#!/usr/bin/python3

import sys
import os
import pytest

module_path = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(module_path)

from ..parser_logo import Parser
from ..language_errors import ParseError, SyntaxError
from ..context import Context
from ..root_context import LogoRootContext
from .test_parser import generate_lexer


def check_context(context: Context, expected_values: dict):
    for key, value in expected_values.items():
        assert context.get_element(key) == value


def check_execution_with_context_validation(list_of_tuples):
    for string, values in list_of_tuples:
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
    check_execution_with_context_validation(zip(TEST_STRINGS, TEST_VALUES))


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
    }), ("x=0 if(23+3>1){x=1} else{x=2}", {
        "x": 1
    })]

    check_execution_with_context_validation(TEST_TUPLES)


def test_functions():
    TEST_TUPLES = [("""glob=0
    x=-3
    fun foo(x)
    {
        x=x+3"""
                    """
        glob=x
    }
    foo(11)
    """, {
                        "glob": 11 + 3,
                        "x": -3
                    }), ("fun foo(){\nreturn()\n}\nfoo()", {}),
                   ("fun foo(){\nreturn(1)\n}\nx=foo()", {
                       "x": 1
                   }),
                   ("""fun fib(num)\n
                   {\n
                   if(num<=1){
                     return(1)
                    }
                    return(fib(num-1)+fib(num-2))
                   \n}

                   x0=fib(0)
                   x1=fib(1)
                   x2=fib(2)
                   x3=fib(3)
                   x4=fib(4)
                   x5=fib(5)
                   """, {
                       "x0": 1,
                       "x1": 1,
                       "x2": 2,
                       "x3": 3,
                       "x4": 5,
                       "x5": 8
                   })]
    check_execution_with_context_validation(TEST_TUPLES)


def test_context():
    root = LogoRootContext()
    root.define_element("x", 0)
    child = Context(parent_context=root)
    child.define_element("x", 1)
    print(root)
    print(child)
    assert child.get_element("x") == root.get_element("x")


def test_standard_libraries():
    TEST_TUPLES = [('print(312) print(4+2) print("slowo") x=True', {
        "x": True
    }), ("t=Turtle() x=t.get_x() t.move(10) t.rotate(30)", {
        "x": 0
    })]
    check_execution_with_context_validation(TEST_TUPLES)
