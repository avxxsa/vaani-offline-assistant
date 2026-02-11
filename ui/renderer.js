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
    openJournalBtn.textContent = "📓 Journal";
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

      // Sidebar control
      if (page === "chat") {
        sidebar?.classList.remove("hidden");
        appRoot?.classList.remove("clean-mode");
        renderChat();
      } else {
        sidebar?.classList.add("hidden");
        appRoot?.classList.add("clean-mode");
      }

      if (page === "todo") {
        sidebar?.classList.add("hidden");
        window.renderTodos?.();

        // Load todo script dynamically
        const script = document.createElement("script");
        script.src = "./scripts/todo.js";
        script.defer = true;
        document.body.appendChild(script);
      }
      if (page === "journal") {
        sidebar?.classList.add("hidden");
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
//python-ui bridge
window.vaani.onPythonMessage(raw => {
  try {
    const msg = JSON.parse(raw);
    const { type, data } = msg;

    console.log("Event:", type, data);

    // STATUS
    if (type === "status") {
      const state = data.state; // Idle, Listening, Processing, Speaking, Calibrating

      if (state === "Listening") {
        showVoiceWave();
      } else if (state === "Processing" || state === "Speaking") {
        freezeVoiceWave();
        if (state === "Speaking" && waveText) waveText.textContent = "Speaking...";
      } else {
        hideVoiceWave();
      }
      return;
    }

    // TRANSCRIPT (User speech)
    if (type === "transcript") {
      if (appMode === "chat") {
        hideVoiceWave();
        storeMessage("user", data.text);
        addBubble("user", data.text);
      }
      return;
    }

    // RESPONSE (Assistant speech)
    if (type === "response") {
      if (appMode === "chat") {
        hideVoiceWave();
        storeMessage("assistant", data.text);
        addBubble("ai", data.text);
      }
      return;
    }

    // ERROR
    if (type === "error") {
      console.error("Backend Error:", data.message);
      // Optionally show a toast
    }

  } catch (e) {
    console.log("Error parsing message:", e, raw);
  }
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

// Chat input handlers
function setupChatInputHandlers() {
  const textInput = document.getElementById("textInput");
  const sendBtn = document.getElementById("sendBtn");
  const micBtn = document.getElementById("micBtn");
  const micStatus = document.getElementById("micStatus");
  
  if (!textInput || !sendBtn || !micBtn) return;

  // Send text message
  function sendMessage() {
    const text = textInput.value.trim();
    if (!text) return;

    textInput.value = "";
    addBubble("user", text);
    storeMessage("user", text);
    
    // Send to Python backend
    window.vaani.sendUserText(text);
  }

  // Send button click
  sendBtn.addEventListener("click", sendMessage);

  // Enter key to send
  textInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });

  // Mic button - press and hold
  let isHolding = false;
  let holdStartTime = 0;
  let autoReleaseTimer = null;
  const MAX_HOLD_DURATION = 5000; // 5 seconds max

  micBtn.addEventListener("mousedown", (e) => {
    e.preventDefault();
    isHolding = true;
    holdStartTime = Date.now();
    micBtn.classList.add("listening");
    micStatus.textContent = "Listening (5s max)...";
    
    // Notify backend to start listening
    window.vaani.startListening?.();
    
    // Auto-release after max duration
    autoReleaseTimer = setTimeout(() => {
      if (isHolding) {
        isHolding = false;
        micBtn.classList.remove("listening");
        micStatus.textContent = "Recording stopped";
        window.vaani.stopListening?.();
      }
    }, MAX_HOLD_DURATION);
  });

  micBtn.addEventListener("mouseup", (e) => {
    e.preventDefault();
    if (autoReleaseTimer) {
      clearTimeout(autoReleaseTimer);
      autoReleaseTimer = null;
    }
    
    if (isHolding) {
      isHolding = false;
      const holdDuration = Date.now() - holdStartTime;
      micBtn.classList.remove("listening");
      micStatus.textContent = holdDuration < 500 ? "Too short" : "";
      
      // Notify backend to stop listening
      window.vaani.stopListening?.();
    }
  });

  // Touch support
  micBtn.addEventListener("touchstart", (e) => {
    e.preventDefault();
    isHolding = true;
    holdStartTime = Date.now();
    micBtn.classList.add("listening");
    micStatus.textContent = "Listening (5s max)...";
    
    window.vaani.startListening?.();
    
    // Auto-release after max duration
    autoReleaseTimer = setTimeout(() => {
      if (isHolding) {
        isHolding = false;
        micBtn.classList.remove("listening");
        micStatus.textContent = "Recording stopped";
        window.vaani.stopListening?.();
      }
    }, MAX_HOLD_DURATION);
  });

  micBtn.addEventListener("touchend", (e) => {
    e.preventDefault();
    if (autoReleaseTimer) {
      clearTimeout(autoReleaseTimer);
      autoReleaseTimer = null;
    }
    
    if (isHolding) {
      isHolding = false;
      const holdDuration = Date.now() - holdStartTime;
      micBtn.classList.remove("listening");
      micStatus.textContent = holdDuration < 500 ? "Too short" : "";
      
      window.vaani.stopListening?.();
    }
  });
}


loadPage("chat").then(() => {
  newChat();
  updateTopbarButton();
  // Setup chat input after page loads
  setTimeout(() => setupChatInputHandlers(), 100);
});

