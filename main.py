#!/usr/bin/python3
import argparse

import pathlib

from tkom_logo.parser_logo import Parser
from tkom_logo.lexer import Lexer
from tkom_logo.shared import ConsoleLogger
from tkom_logo.text_reader import FileReader
from tkom_logo.language_errors import BaseLanguageException

from tkom_logo.standard_library.drawing.window_renderer import WindowRenderer

logger = ConsoleLogger()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Simple logo-like language interpreter")

    parser.add_argument("file",
                        help="path to file with code",
                        type=pathlib.Path)
    parser.add_argument("-n",
                        "--no-render",
                        help="Don't show turtle visualization after execution",
                        action="store_false",
                        dest="render")

    return parser.parse_args()


def render(program):
    c = program.get_canvas()
    renderer = WindowRenderer(c)
    renderer.render()


def main():
    args = parse_arguments()
    if not args.file.exists():
        logger.warn(f"File {args.file} does not exist")
        return
    logger.info("Parsing program")
    reader = FileReader(args.file)
    lexer = Lexer(reader)
    program = Parser(lexer).parse_program()
    logger.info("Executing program")
    try:
        program.execute()
        if args.render:
            render(program)
        else:
            logger.info("Pass rendering")
    except BaseLanguageException as exc:
        logger.error(f"Error: {exc.args[0]}")
        logger.error(f"At: {exc.location}")


if __name__ == "__main__":
    main()
