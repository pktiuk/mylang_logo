#!/usr/bin/python3

import sys
import os
import pytest

module_path = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(module_path)

from ..parser_logo import Parser
from ..language_errors import ParseError, SyntaxError
from ..text_reader import StringReader
from ..lexer import Lexer


def generate_lexer(text) -> Lexer:
    buf = StringReader(text)
    lexer = Lexer(buf)

    return lexer


def test_parser_stability():
    TEST_STRINGS = [
        "(-33*1)/-2", "2+3*4", "23==3&& 5>2", "2=3&& 5>2", "-a +3",
        "funkcja()+32", "a > 43 && var==4 || obj.get() != 12"
    ]
    for string in TEST_STRINGS:
        print(f'parsing string: {string}')
        q = generate_lexer(string)
        p = Parser(token_source=q)
        result = p.parse()
        print(result)


def test_multiplications():
    q = generate_lexer("22*4/3*1")
    p = Parser(token_source=q)
    result = p.parse()
    print(result)


def test_functions():
    TEST_STRINGS = [
        "f1()()()", "f2(arg1)", "f3(2+3*5)", "f4(32,43-34)", "f5(1*(2+3))",
        "f6(1*2*(4+5),32,val1)", "fun foo(){" + "}", "fun foo2(arg1) {" + "}",
        "fun foo3(arg1, arg2) {" + "}", "fun foo4(arg1, arg2) {x = 54+2" + "}",
        "fun foo5() {x = 34 x = x +3" + "}", "fun foo6(num1){\n" + """
        tmp = 43
        tmp = tmp - arg
        print(tmp)}"""
    ]
    for string in TEST_STRINGS:
        print(f'parsing string: {string}')
        q = generate_lexer(string)
        p = Parser(token_source=q)
        result = p.parse()
        print(result)


def test_loops():
    TEST_STRINGS = [
        "while(true){" + "}", "while(3<43){" + "}",
        "while(true){ x = x+1" + "}"
    ]
    for string in TEST_STRINGS:
        print(f'parsing string: {string}')
        q = generate_lexer(string)
        p = Parser(token_source=q)
        result = p.parse()
        print(result)


def test_ifs():
    TEST_STRINGS = [
        "if(true){" + "}",
        "if(3<43 && is_checked==1){" + "}",
        "if(true){ x = x+1" + "}else{" + "print(msg)}",
    ]
    for string in TEST_STRINGS:
        print(f'parsing string: {string}')
        q = generate_lexer(string)
        p = Parser(token_source=q)
        result = p.parse()
        print(result)


def test_field_operators():
    TEST_STRINGS = [
        "turtle.print()", "turtle.move(4231)", "something.get_elem().value"
    ]
    for string in TEST_STRINGS:
        print(f'parsing string: {string}')
        q = generate_lexer(string)
        p = Parser(token_source=q)
        result = p.parse()
        print(result)


def test_exceptions():
    q = generate_lexer("while True")
    p = Parser(token_source=q)
    with pytest.raises(SyntaxError, match="opening paren"):
        p.parse()
    q = generate_lexer("if value")
    p = Parser(token_source=q)
    with pytest.raises(SyntaxError, match="opening paren"):
        p.parse()
    q = generate_lexer("thh.field.()")
    p = Parser(token_source=q)
    with pytest.raises(SyntaxError, match="after dot"):
        p.parse()


def test_program_parsing():
    q = generate_lexer("fun f1(){" + "}x = 32 foo(x+1)")
    p = Parser(token_source=q)
    prog = p.parse_program()
    print(prog)
