#!/usr/bin/python3

from flask import Flask, request

from mylang.shared import StringLogger, set_global_logger, get_global_logger

from mylang.language_errors import LogoSyntaxError, BaseLanguageException
from mylang.lexer import Lexer
from mylang.parser_logo import Parser
from mylang.text_reader import StringReader

app = Flask(__name__)

set_global_logger(StringLogger())


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
    response["log"] = log
    response["canvas"] = None
    response["error"] = error
    return response


def execute_code(code: str):
    reader = StringReader(code)
    lexer = Lexer(reader, get_global_logger())
    try:
        program = Parser(lexer, get_global_logger()).parse_program()
        program.execute()
    except BaseLanguageException as exc:
        error_msg = f"Error: {str(exc)}\n"
        error_msg += f"At: {exc.location}\n"
        error_msg += reader.get_loc_region(exc.location)
        return ("", None, error_msg)

    canvas = program.get_canvas()
    return (get_global_logger().out_string, None, None)  #TODO draw canvas


if __name__ == '__main__':
    app.run()
