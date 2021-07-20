"use strict";

const btn_execute = document.getElementById("btn_execute");
const code_area = document.getElementById("code_area");
const log_area = document.getElementById("log_area");
const mylang_canvas = document.getElementById("mylang_canvas");

class Renderer {
  constructor(canvas_element) {
    if (!mylang_canvas.getContext) {
      //TODO exception
    }
    this.canvas = canvas_element;
    this.context = canvas_element.getContext("2d");
    this.rescale();
  }
  rescale() {
    this.context.translate(this.canvas.width / 2, this.canvas.height / 2);
    this.context.scale(this.canvas.width / this.canvas.height, 1);
  }
  draw(paths) {
    this.context.beginPath();
    this.context.moveTo(0, 0);
    this.context.lineTo(30, 30);
    this.context.closePath();
    this.context.stroke();
  }
}

const renderer = new Renderer(mylang_canvas);

const handle_execution_result = function (result) {
  if (result["error"] == null) {
    log_area.textContent = result["log"];
    renderer.draw(result["canvas"]);
  } else {
    log_area.innerHTML =
      "<div style='color: red'>" +
      result["error"].replaceAll("\n", "<br>") +
      "</div>";
  }
  console.log(result);
};

btn_execute.addEventListener("click", function () {
  console.log("Execute code: " + code_area.value);

  fetch("http://127.0.0.1:5000", {
    method: "post",
    headers: {
      Accept: "application/json, text/plain",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code: code_area.value }),
  })
    .then((res) => res.json())
    .then(function (result) {
      console.log("got result:");
      console.log(result);
      handle_execution_result(result);
    });
});
