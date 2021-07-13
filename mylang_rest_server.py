#!/usr/bin/python3

from flask import Flask, request

from mylang.language_errors import LogoSyntaxError, BaseLanguageException
from mylang.lexer import Lexer
from mylang.parser_logo import Parser
from mylang.text_reader import StringReader

app = Flask(__name__)


@app.route('/', methods=["GET"])
def get_root():
    print("get")
    # TODO return a simple website
    return "Hello"


@app.route('/', methods=["POST"])
def post_code():
    print("Post")
    print(request.form)
    parsed_json = request.get_json()
    code = parsed_json["code"]
    print("Got code: ", code, "\nexecuting...")

    log, canvas, error = execute_code(code)
    response = {}
    response["log"] = "hello"
    response["canvas"] = None
    response["error"] = error
    return response


def execute_code(code: str):
    reader = StringReader(code)
    lexer = Lexer(reader)
    try:
        program = Parser(lexer).parse_program()
        program.execute()
    except LogoSyntaxError as err:
        return ("", None, err.str())
    except BaseLanguageException as exc:
        error_msg = f"Error: {exc.args[0]}"
        error_msg += f"At: {exc.location}"
        error_msg += reader.get_loc_region(exc.location)
        return ("", None, error_msg)
    return ("finished", None, "")  #TODO


if __name__ == '__main__':
    app.run()
