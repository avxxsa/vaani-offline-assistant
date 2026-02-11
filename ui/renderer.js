console.log("Renderer loaded");

//DOM roots

const recentList = document.getElementById("recentList");
const newChatBtn = document.getElementById("newChatBtn");
const openJournalBtn = document.getElementById("openJournalBtn");
const sidebar = document.getElementById("sidebar");
const appRoot = document.querySelector(".app");
const openTodoBtn = document.getElementById("openTodoBtn");

//state

let appMode = "chat";

let chatMessages = null;
let voiceWave = null;
let waveText = null;

let chats = [];
let currentChatId = null;

// Mic waveform state
let audioContext = null;
let analyser = null;
let micSource = null;
let animationId = null;

function scrollToBottom() {
  if (!chatMessages) return;
  requestAnimationFrame(() => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  });
}

function updateTopbarButton() {
  if (!openJournalBtn || !openTodoBtn) return;

  if (appMode === "chat") {
    openJournalBtn.textContent = "Journal";
    openJournalBtn.style.display = "inline-flex";
    openTodoBtn.style.display = "inline-flex";
  }

  if (appMode === "journal" || appMode === "todo") {
    openJournalBtn.textContent = "← Back to Chat";
    openJournalBtn.style.display = "inline-flex";
    openTodoBtn.style.display = "none";
  }
}

//page loader 
function loadPage(page) {
  return fetch(`./pages/${page}.html`)
    .then(res => res.text())
    .then(html => {
      document.getElementById("app").innerHTML = html;

      // Cache page DOM
      chatMessages = document.getElementById("chatMessages");
      voiceWave = document.getElementById("voiceWave");
      waveText = document.getElementById("waveText");

      // Sidebar + Layout control

      if (page === "chat") {
        document.body.classList.remove("journal-mode");
        sidebar?.classList.remove("hidden");
        appRoot?.classList.remove("clean-mode");   // keep this
        renderChat();
      }

      if (page === "todo") {
        document.body.classList.remove("journal-mode");  // 🔥 ADD THIS
        sidebar?.classList.add("hidden");
        appRoot?.classList.add("clean-mode");            // 🔥 ADD THIS
        window.renderTodos?.();

        // Load todo script dynamically
        const script = document.createElement("script");
        script.src = "./scripts/todo.js";
        script.defer = true;
        document.body.appendChild(script);
      }

      if (page === "journal") {
        document.body.classList.add("journal-mode");
        sidebar?.classList.add("hidden");
        appRoot?.classList.add("clean-mode");     // 🔥 THIS WAS MISSING
        window.renderJournal?.();
      }

    });
}


//chat

function addBubble(sender, text) {
  if (!chatMessages) return;

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${sender === "user" ? "user" : "ai"}`;
  bubble.textContent = text;

  chatMessages.appendChild(bubble);
  scrollToBottom();
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
  if (!chatMessages) return;

  chatMessages.innerHTML = "";
  const chat = chats.find(c => c.id === currentChatId);
  if (!chat) return;

  chat.messages.forEach(m => addBubble(m.sender, m.text));
}

//sidebar

function renderSidebar() {
  if (!recentList) return;
  recentList.innerHTML = "";

  chats.forEach(chat => {
    const item = document.createElement("div");
    item.className = "recent-item";
    if (chat.id === currentChatId) item.classList.add("active");

    item.innerHTML = `
      <div class="recent-dot"></div>
      <div class="title">${chat.title}</div>
    `;

    item.onclick = () => {
      currentChatId = chat.id;
      renderSidebar();
      renderChat();
    };

    recentList.appendChild(item);
  });
}

function newChat() {
  const chat = { id: Date.now(), title: "New Chat", messages: [] };
  chats.unshift(chat);
  currentChatId = chat.id;
  renderSidebar();
  renderChat();
}

//voicewave
function showVoiceWave() {
  if (!voiceWave) return;
  voiceWave.classList.remove("hidden", "processing");
  waveText.textContent = "Listening…";
  startMicWave();
}

function freezeVoiceWave() {
  if (!voiceWave) return;
  voiceWave.classList.add("processing");
  waveText.textContent = "Processing…";
  stopMicWave();
}

function hideVoiceWave() {
  if (!voiceWave) return;
  stopMicWave();
  voiceWave.classList.add("hidden");
}

//mic animation

async function startMicWave() {
  if (audioContext || !voiceWave) return;

  audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  micSource = audioContext.createMediaStreamSource(stream);
  analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;
  micSource.connect(analyser);

  const dataArray = new Uint8Array(analyser.frequencyBinCount);

  function animate() {
    analyser.getByteFrequencyData(dataArray);
    const bars = voiceWave.querySelectorAll(".wave span");

    bars.forEach((bar, i) => {
      const value = dataArray[i * 2] || 0;
      bar.style.height = `${Math.max(6, value / 3)}px`;
    });

    animationId = requestAnimationFrame(animate);
  }

  animate();
}

function stopMicWave() {
  if (animationId) cancelAnimationFrame(animationId);
  micSource?.mediaStream.getTracks().forEach(t => t.stop());
  audioContext?.close();
  audioContext = analyser = micSource = animationId = null;
}

//python-ui bridge
window.vaani.onPythonMessage(raw => {
  raw.split("\n").filter(Boolean).forEach(line => {
    try {
      const msg = JSON.parse(line);

      if (msg.type === "status") {
        if (msg.data === "listening") showVoiceWave();
        if (msg.data === "processing") freezeVoiceWave();
        return;
      }

      if (appMode === "chat") {
        if (msg.type === "user") {
          hideVoiceWave();
          storeMessage("user", msg.data);
          addBubble("user", msg.data);
        }
        if (msg.type === "assistant") {
          hideVoiceWave();
          storeMessage("assistant", msg.data);
          addBubble("ai", msg.data);
        }
      }

  /*  if(appMode === "journal" && msg.type === "user") {
        hideVoiceWave();
        addJournalEntry(msg.data);
      } */

    } catch {
      console.log("Non-JSON:", line);
    }
  });
});

// journal

function bindJournalUI() {
}

function addJournalEntry(text) {
  const list = document.getElementById("journalList");
  if (!list) return;

  const entry = document.createElement("div");
  entry.className = "journal-entry";

  entry.innerHTML = `
    <div class="time">${new Date().toLocaleString()}</div>
    <div class="text">${text}</div>
  `;

  list.prepend(entry);
}

//init

newChatBtn?.addEventListener("click", newChat);

openJournalBtn?.addEventListener("click", () => {
  if (appMode === "chat") {
    appMode = "journal";
    loadPage("journal");
  } else {
    appMode = "chat";
    loadPage("chat");
  }

  updateTopbarButton();
});


openTodoBtn?.addEventListener("click", () => {
  appMode = "todo";
  loadPage("todo");
  updateTopbarButton();
});



loadPage("chat").then(() => {
  newChat();
  updateTopbarButton();
});

