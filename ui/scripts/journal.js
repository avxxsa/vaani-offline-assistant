// Load journal entries from backend
async function renderJournal() {
  const list = document.getElementById("journalList");
  if (!list) return;

  list.innerHTML = "<p style='text-align: center; color: rgba(255,255,255,0.5); padding: 20px;'>Loading journal...</p>";

  try {
    const entries = await window.vaani.requestData("journal");
    
    list.innerHTML = "";

    if (!entries || entries.length === 0) {
      list.innerHTML = "<p style='text-align: center; color: rgba(255,255,255,0.5); padding: 20px;'>No journal entries yet. Start speaking!</p>";
      return;
    }

    entries.forEach(entry => {
      const div = document.createElement("div");
      div.className = "journal-entry";

      // Handle both old string format and new object format
      const text = typeof entry === "string" ? entry : entry.text || "";
      const time = typeof entry === "string" ? "Unknown" : entry.time || "Unknown";

      div.innerHTML = `
        <div class="time">${time}</div>
        <div class="text">${text}</div>
      `;

      list.appendChild(div);
    });
  } catch (e) {
    console.error("Error loading journal:", e);
    list.innerHTML = "<p style='text-align: center; color: red; padding: 20px;'>Error loading journal</p>";
  }
}

window.renderJournal = renderJournal;
