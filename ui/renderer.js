console.log("Renderer loaded");

const chatMessages = document.getElementById("chatMessages");
const recentList = document.getElementById("recentList");
const newChatBtn = document.getElementById("newChatBtn");

let chats = [];
let currentChatId = null;

function addBubble(sender, text) {
  const bubble = document.createElement("div");
  bubble.classList.add("chat-bubble", sender === "user" ? "user" : "ai");
  bubble.textContent = text;

  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function storeMessage(sender, text) {
  const chat = chats.find(c => c.id === currentChatId);
  if (!chat) return;

  chat.messages.push({ sender, text });

  if (chat.title === "New Chat" && sender === "user") {
    chat.title = text.slice(0, 30);
    renderSidebar();
  }
}

function renderChat() {
  chatMessages.innerHTML = "";

  const chat = chats.find(c => c.id === currentChatId);
  if (!chat) return;

  chat.messages.forEach(m => {
    const bubble = document.createElement("div");
    bubble.classList.add("chat-bubble", m.sender === "user" ? "user" : "ai");
    bubble.textContent = m.text;
    chatMessages.appendChild(bubble);
  });

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderSidebar() {
  recentList.innerHTML = "";

  chats.forEach(chat => {
    const item = document.createElement("div");
    item.className = "recent-item";
    item.innerHTML = `
      <div class="recent-dot"></div>
      <div>
        <div class="title">${chat.title}</div>
      </div>
    `;

    item.onclick = () => {
      currentChatId = chat.id;
      renderChat();
    };

    recentList.appendChild(item);
  });
}

function newChat() {
  const chat = {
    id: Date.now(),
    title: "New Chat",
    messages: []
  };

  chats.unshift(chat);
  currentChatId = chat.id;

  renderSidebar();
  renderChat();
}

window.vaani.onPythonMessage((raw) => {
  const lines = raw.split("\n").map(l => l.trim()).filter(Boolean);

  for (const line of lines) {
    try {
      const msg = JSON.parse(line);

      if (msg.type === "user") {
        addBubble("user", msg.data);
        storeMessage("user", msg.data);
      }

      if (msg.type === "assistant") {
        addBubble("ai", msg.data);
        storeMessage("assistant", msg.data);
      }

      if (msg.type === "status") {
        console.log("Status:", msg.data);
      }

    } catch (e) {
      console.log("Non-JSON:", line);
    }
  }
});


newChatBtn.addEventListener("click", newChat);

newChat();
