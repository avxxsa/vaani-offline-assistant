// Load todos from backend
async function renderTodos() {
  const leftCol = document.getElementById("todoLeft");
  const rightCol = document.getElementById("todoRight");

  if (!leftCol || !rightCol) return;

  leftCol.innerHTML = "<p style='text-align: center; color: rgba(255,255,255,0.5);'>Loading...</p>";
  rightCol.innerHTML = "";

  try {
    const todos = await window.vaani.requestData("todos");
    
    leftCol.innerHTML = "";
    rightCol.innerHTML = "";

    if (!todos || todos.length === 0) {
      leftCol.innerHTML = "<p style='text-align: center; color: rgba(255,255,255,0.5);'>No todos yet!</p>";
      return;
    }

    todos.forEach((task, index) => {
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
  } catch (e) {
    console.error("Error loading todos:", e);
    leftCol.innerHTML = "<p style='text-align: center; color: red;'>Error loading todos</p>";
  }
}

window.renderTodos = renderTodos;
