#!/usr/bin/python3

from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "GET":
        return "Hello"

    if request.method == "POST":
        return "you requested something" + str(request.form)

    return ""


if __name__ == '__main__':
    app.run()
