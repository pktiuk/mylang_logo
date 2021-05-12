#!/usr/bin/python3

import sys
import os
import pytest
from queue import Queue

module_path = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(module_path)

from shared import Token, TokenType, Location, ParserNode
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


def check_leaves_and_nodes(tree: ParserNode, print_tree=True):
    """Leaves in tree can be only values,
    middle nodes can be only operators
    """
    LEAF_TOKENS = [
        TokenType.CONST, TokenType.IDENTIFIER, TokenType.OPEN_BLOCK,
        TokenType.ELSE
    ]
    NODE_TOKENS = [
        TokenType.ADD_OPERATOR, TokenType.MULT_OPERATOR,
        TokenType.UNARY_OPERATOR, TokenType.OR_OPERATOR,
        TokenType.AND_OPERATOR, TokenType.COMP_OPERATOR,
        TokenType.FIELD_OPERATOR, TokenType.ASSIGNMENT_OPERATOR, TokenType.IF,
        TokenType.WHILE, TokenType.FUN, TokenType.FUN_OPERATOR,
        TokenType.OPEN_BLOCK
    ]
    NOT_ALLOWED_TOKENS = [TokenType.EOF, TokenType.EOL]
    if print_tree:
        print(tree)

    if tree.token.symbol_type in NOT_ALLOWED_TOKENS:
        raise ValueError("Not allowed token in tree")

    if tree.get_depth() == 0:
        if tree.token.symbol_type not in LEAF_TOKENS:
            raise ValueError("Wrong value of leaf token")
    else:
        if tree.token.symbol_type not in NODE_TOKENS:
            raise ValueError("Wrong value of middle node token")
        for child in tree.children:
            check_leaves_and_nodes(child, False)


def test_parser_stability():
    TEST_STRINGS = [
        "(-33*1)/-2", "2+3*4", "23==3&& 5>2", "2=3&& 5>2", "-a +3",
        "funkcja()+32"
    ]
    for string in TEST_STRINGS:
        print(f'parsing string: {string}')
        q = generate_queue(string)
        p = Parser(token_source=q)
        result = p.parse()
        check_leaves_and_nodes(result)


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
    check_leaves_and_nodes(result)
    assert result.token.value == "*"
    assert result.children[1].token == tokens[-2]


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
        q = generate_queue(string)
        p = Parser(token_source=q)
        result = p.parse()
        check_leaves_and_nodes(result)


def test_loops():
    TEST_STRINGS = [
        "while(true){" + "}", "while(3<43){" + "}",
        "while(true){ x = x+1" + "}"
    ]
    for string in TEST_STRINGS:
        print(f'parsing string: {string}')
        q = generate_queue(string)
        p = Parser(token_source=q)
        result = p.parse()
        check_leaves_and_nodes(result)


def test_ifs():
    TEST_STRINGS = [
        "if(true){" + "}",
        "if(3<43 && is_checked){" + "}",
        "if(true){ x = x+1" + "}else{" + "print(msg)}",
    ]
    for string in TEST_STRINGS:
        print(f'parsing string: {string}')
        q = generate_queue(string)
        p = Parser(token_source=q)
        result = p.parse()
        check_leaves_and_nodes(result)


def test_field_operators():
    TEST_STRINGS = [
        "turtle.print()", "turtle.move(4231)", "something.get_elem().value"
    ]
    for string in TEST_STRINGS:
        print(f'parsing string: {string}')
        q = generate_queue(string)
        p = Parser(token_source=q)
        result = p.parse()
        check_leaves_and_nodes(result)