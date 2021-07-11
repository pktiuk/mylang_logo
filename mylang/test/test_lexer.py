#!/usr/bin/python3

import sys
import os
import pytest

module_path = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(module_path)

from ..shared import Token, TokenType, Location
from ..lexer import Lexer
from ..language_errors import UnexpectedCharacterError, ParseError
from ..text_reader import StringReader





def test_lexer():
    t = StringReader("""<=(\"word\"+         312.543/1322(

    ))""")
    lexer = Lexer(source=t)
    assert lexer.get_token() == Token(TokenType.COMP_OPERATOR, "<=",
                                      Location(0, 0))
    assert lexer.get_token() == Token(TokenType.OPEN_PAREN, "(",
                                      Location(0, 2))
    assert lexer.get_token() == Token(TokenType.CONST, 'word', Location(0, 3))
    assert lexer.get_token() == Token(TokenType.ADD_OPERATOR, "+",
                                      Location(0, 9))
    assert lexer.get_token() == Token(TokenType.CONST, 312.543,
                                      Location(0, 19))
    assert lexer.get_token() == Token(TokenType.MULT_OPERATOR, "/",
                                      Location(0, 26))
    assert lexer.get_token() == Token(TokenType.CONST, 1322, Location(0, 27))
    assert lexer.get_token() == Token(TokenType.OPEN_PAREN, "(",
                                      Location(0, 31))
    assert lexer.get_token() == Token(TokenType.CLOSE_PAREN, ")",
                                      Location(2, 4))
    assert lexer.get_token() == Token(TokenType.CLOSE_PAREN, ")",
                                      Location(2, 5))


def test_lexer_assignment():
    t = StringReader("""n=432+32-0+-32""")
    lexer = Lexer(source=t)
    assert lexer.get_token() == Token(TokenType.IDENTIFIER, "n",
                                      Location(0, 0))
    assert lexer.get_token() == Token(TokenType.ASSIGNMENT_OPERATOR, "=",
                                      Location(0, 1))
    assert lexer.get_token() == Token(TokenType.CONST, 432, Location(0, 2))
    assert lexer.get_token() == Token(TokenType.ADD_OPERATOR, "+",
                                      Location(0, 5))
    assert lexer.get_token() == Token(TokenType.CONST, 32, Location(0, 6))
    assert lexer.get_token() == Token(TokenType.ADD_OPERATOR, "-",
                                      Location(0, 8))
    assert lexer.get_token() == Token(TokenType.CONST, 0, Location(0, 9))
    assert lexer.get_token() == Token(TokenType.ADD_OPERATOR, "+",
                                      Location(0, 10))
    assert lexer.get_token() == Token(TokenType.ADD_OPERATOR, "-",
                                      Location(0, 11))
    assert lexer.get_token() == Token(TokenType.CONST, 32, Location(0, 12))


def test_number_parsing():
    t = StringReader("0")
    lexer = Lexer(source=t)
    assert lexer.get_token() == Token(TokenType.CONST, 0, Location(0, 0))

    t = StringReader("0.12")
    lexer = Lexer(source=t)
    assert lexer.get_token() == Token(TokenType.CONST, 0.12, Location(0, 0))

    t = StringReader("1312.43ls")
    lexer = Lexer(source=t)
    with pytest.raises(UnexpectedCharacterError):
        print(lexer.get_token())

    s = StringReader("1312.")
    lexer = Lexer(source=s)
    with pytest.raises(ParseError):
        print(lexer.get_token())

    s = StringReader("032")
    lexer = Lexer(source=s)
    with pytest.raises(ParseError):
        print(lexer.get_token())


def test_wrong_identifiers():
    s = StringReader("1ls")
    lexer = Lexer(source=s)
    with pytest.raises(UnexpectedCharacterError):
        print(lexer.get_token())


def test_proper_EOF():
    s = StringReader("")
    lexer = Lexer(source=s)
    assert lexer.get_token().symbol_type == TokenType.EOF

    s = StringReader("    ")
    lexer = Lexer(source=s)
    assert lexer.get_token().symbol_type == TokenType.EOF

    s = StringReader("  \n  ")
    lexer = Lexer(source=s)
    lexer.get_token()
    assert lexer.get_token().symbol_type == TokenType.EOF

    s = StringReader('   "beginning of string123')
    lexer = Lexer(source=s)
    with pytest.raises(EOFError):
        lexer.get_token()


def test_big_text():
    s = StringReader("""fun draw_square(len,len2)
{
  i = 0
  t = Turtle()
  while(i<=3)
  {
    t.fd(len)
    t.rt(90)
    i=i+1
  }
  pole = len*len
  return(pole)
}

print("Obrysowane pole ")

pole=draw_square(10)

msg = ""

if(pole > 10 && pole <200)
{
  print("jest wieksze od 10 i mniejsze od 200")
}else
{
  print("jest inne niz przewidywane")
}
  """)

    lexer = Lexer(source=s)

    tokens = []
    for i in range(90):
        tokens.append(lexer.get_token())

    assert tokens[87].symbol_type == TokenType.EOF
    assert tokens[86].symbol_type != TokenType.EOF
