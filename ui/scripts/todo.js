// dummy data 

const dummyTodos = [
  "Finish UI for Vaani",
  "Prepare project logsheet",
  "Review renderer.js",
  "OS lab report",
  "study for compart",
  "cry",
  "huhuhu",
  "Prepare viva explanation"
];

function renderTodos() {
  const leftCol = document.getElementById("todoLeft");
  const rightCol = document.getElementById("todoRight");

  if (!leftCol || !rightCol) return;

  leftCol.innerHTML = "";
  rightCol.innerHTML = "";

  dummyTodos.forEach((task, index) => {
  const item = document.createElement("div");
  item.className = "todo-item";

  item.innerHTML = `
    <span class="checkbox"></span>
    <span class="line">${task}</span>
  `;

  item.addEventListener("click", () => {
    item.classList.toggle("completed");
  });

  (index % 2 === 0 ? leftCol : rightCol).appendChild(item);
});

}

window.renderTodos = renderTodos;
