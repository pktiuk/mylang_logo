import pytest

from ..parser_logo import Parser
from ..shared import Location
from ..text_reader import StringReader
from ..lexer import Lexer


def generate_lexer(text) -> Lexer:
    buf = StringReader(text)
    lexer = Lexer(buf)
    return lexer


def check_exception(function,
                    ex_type,
                    match: str = "",
                    loc: Location = None):
    with pytest.raises(ex_type, match=match):
        try:
            function()
        except ex_type as err:
            if loc:
                errloc = err.location
                assert loc == errloc
            raise err


def check_parse_exception(program_str: str,
                          ex_type,
                          match: str = "",
                          loc: Location = None):
    q = generate_lexer(program_str)
    p = Parser(token_source=q)
    check_exception(p.parse_program, ex_type, match, loc)


def check_execution_exception(program_str: str,
                              ex_type,
                              match: str = "",
                              loc: Location = None):
    q = generate_lexer(program_str)
    p = Parser(token_source=q)
    prog = p.parse_program()
    check_exception(prog.execute, ex_type, match, loc)
