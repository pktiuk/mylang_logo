const btn_execute = document.getElementById("btn_execute");
const code_area = document.getElementById("code_area");
const log_area = document.getElementById("log_area");

btn_execute.addEventListener("click", function () {
  console.log("Execute code");

  fetch("http://127.0.0.1:5000", {
    method: "post",
    headers: {
      Accept: "application/json, text/plain",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code: code_area.textContent }),
  })
    .then((res) => res.json())
    .then(function (result) {
      console.log("got result:");
      console.log(result);
      log_area.textContent = result["log"];
    });
});
