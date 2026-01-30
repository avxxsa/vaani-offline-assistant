console.log("Renderer loaded");

const chatMessages = document.getElementById("chatMessages");
const recentList = document.getElementById("recentList");
const newChatBtn = document.getElementById("newChatBtn");
const voiceWave = document.getElementById("voiceWave");
const waveText = document.getElementById("waveText");


let chats = [];
let currentChatId = null;

//Mic waveform state
let audioContext = null;
let analyser = null;
let micSource = null;
let animationId = null;

//auto scroll
function scrollToBottom() {
  setTimeout(() => {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }, 0);
}


// Chat helpers 
function addBubble(sender, text) {
  const bubble = document.createElement("div");
  bubble.classList.add("chat-bubble", sender === "user" ? "user" : "ai");
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

// Bottom wave controls 
function showVoiceWave() {
  if (!voiceWave) return;
  voiceWave.classList.remove("hidden", "processing");
  if (waveText) waveText.textContent = "Listening…";
  startMicWave();
}

function freezeVoiceWave() {
  if (!voiceWave) return;
  voiceWave.classList.add("processing");
  if (waveText) waveText.textContent = "Processing…";
  stopMicWave();
}

function hideVoiceWave() {
  stopMicWave();
  if (voiceWave) voiceWave.classList.add("hidden");
}

// Real mic waveform 
async function startMicWave() {
  if (audioContext) return;

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
  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }

  if (micSource?.mediaStream) {
    micSource.mediaStream.getTracks().forEach(t => t.stop());
  }

  if (audioContext) audioContext.close();

  audioContext = null;
  analyser = null;
  micSource = null;
}


function renderChat() {
  chatMessages.innerHTML = "";
  const chat = chats.find(c => c.id === currentChatId);
  if (!chat) return;

  chat.messages.forEach(m => addBubble(m.sender, m.text));
  scrollToBottom();
}

// Sidebar
function renderSidebar() {
  recentList.innerHTML = "";

  chats.forEach(chat => {
    const item = document.createElement("div");
    item.className = "recent-item";

    if (chat.id === currentChatId) {
      item.classList.add("active");
    }

    item.innerHTML = `
      <div class="recent-dot"></div>
      <div class="title">${chat.title}</div>
    `;

    item.onclick = () => {
      currentChatId = chat.id;
      renderSidebar();   //  important
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

//python-UI 
window.vaani.onPythonMessage((raw) => {
  raw.split("\n").filter(Boolean).forEach(line => {
    try {
      const msg = JSON.parse(line);

      if (msg.type === "status") {
        if (msg.data === "listening") showVoiceWave();
        if (msg.data === "processing") freezeVoiceWave();
      }

      if (msg.type === "user") {
        hideVoiceWave();
        addBubble("user", msg.data);
        storeMessage("user", msg.data);
      }

      if (msg.type === "assistant") {
        hideVoiceWave();
        addBubble("ai", msg.data);
        storeMessage("assistant", msg.data);
      }

    } catch {
      console.log("Non-JSON:", line);
    }
  });
});

// Init 
newChatBtn.addEventListener("click", newChat);
newChat();
