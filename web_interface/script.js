"use strict";

const btn_execute = document.getElementById("btn_execute");
const code_area = document.getElementById("code_area");
const log_area = document.getElementById("log_area");
const mylang_canvas = document.getElementById("mylang_canvas");

class Renderer {
  constructor(canvas_element) {
    this.svg = canvas_element;
  }
  draw(paths) {
    this.svg.innerHTML = "";

    for (const key in paths.turtle_angles) {
      let iter = paths.turtle_lines[key].values();
      let start_x = null;
      let start_y = null;

      let result = iter.next();
      [start_x, start_y] = result.value;
      result = iter.next();

      while (!result.done) {
        let [x, y] = result.value;
        this.draw_line(start_x, start_y, x, y);
        [start_x, start_y] = [x, y];
        result = iter.next();
      }
      if (paths.turtle_angles[key] !== null) {
        this.draw_turtle(start_x, start_y, paths.turtle_angles[key]);
      }
    }
  }
  draw_line(x1, y1, x2, y2) {
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", x1);
    line.setAttribute("y1", y1);
    line.setAttribute("x2", x2);
    line.setAttribute("y2", y2);
    line.setAttribute("class", "path-line");

    this.svg.insertAdjacentElement("beforeend", line);
  }
  draw_turtle(x, y, angle) {
    const size = 10;
    const turtle = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "image"
    );
    turtle.setAttribute("class", "turtle");
    turtle.setAttribute("x", x - size / 2);
    turtle.setAttribute("y", y - size / 2);
    turtle.setAttribute(
      "href",
      "https://raw.githubusercontent.com/ros/ros_tutorials/noetic-devel/turtlesim/images/box-turtle.png"
    );
    turtle.setAttribute("width", size);
    turtle.setAttribute("height", size);
    turtle.style.transform = `rotate(${angle + 180}deg)`;

    this.svg.insertAdjacentElement("beforeend", turtle);
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
  //TODO handle exception
  fetch("http://srv08.mikr.us:40195", {
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
