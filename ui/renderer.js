console.log("Renderer loaded");

const chatMessages = document.getElementById("chatMessages");
const recentList = document.getElementById("recentList");
const newChatBtn = document.getElementById("newChatBtn");

let chats = [];
let currentChatId = null;
let listeningBubble = null;


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

function showListeningBubble(text = "Listening…") {
  if (listeningBubble) return;

  listeningBubble = document.createElement("div");
  listeningBubble.classList.add("chat-bubble", "user", "listening");
  listeningBubble.textContent = text;

  chatMessages.appendChild(listeningBubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateListeningBubble(text) {
  if (listeningBubble) {
    listeningBubble.textContent = text;
  }
}

function removeListeningBubble() {
  if (listeningBubble) {
    listeningBubble.remove();
    listeningBubble = null;
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

      // USER FINAL TEXT
      if (msg.type === "user") {
        removeListeningBubble();
        addBubble("user", msg.data);
        storeMessage("user", msg.data);
      }

      // ASSISTANT RESPONSE
      if (msg.type === "assistant") {
        removeListeningBubble();
        addBubble("ai", msg.data);
        storeMessage("assistant", msg.data);
      }

      // STATUS UPDATES
      if (msg.type === "status") {
        if (msg.data === "listening") {
          showListeningBubble("Listening…");
        }

        if (msg.data === "processing") {
          updateListeningBubble("Processing…");
        }
      }

    } catch (e) {
      console.log("Non-JSON:", line);
    }
  }
});


newChatBtn.addEventListener("click", newChat);

newChat();
