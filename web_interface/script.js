const btn_execute = document.getElementById("btn_execute");
const code_area = document.getElementById("code_area");
const log_area = document.getElementById("log_area");

const handle_execution_result = function (result) {
  if (result["error"] == null) {
    log_area.textContent = result["log"];
  } else {
    log_area.innerHTML =
      "<div style='color: red'>" +
      result["error"].replaceAll("\n", "<br>") +
      "</div>";
  }
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
