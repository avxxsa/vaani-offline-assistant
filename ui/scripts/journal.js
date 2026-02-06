// Dummy journal entries
const dummyJournalEntries = [
  {
    text: "Today felt productive. I finally finished the UI work.",
    time: "Feb 3,2026 · 10:12 PM"
  },
  {
    text: "Worked on separating frontend and backend. Learned a lot.",
    time: "Feb 6, 2026 · 9:40 PM"
  },
  {
    text: "The to-do list UI is finally coming together nicely.",
    time: "Feb 6, 2026 · 8:55 PM"
  }
];

function renderJournal() {
  const list = document.getElementById("journalList");
  if (!list) return;

  list.innerHTML = "";

  dummyJournalEntries.forEach(entry => {
    const div = document.createElement("div");
    div.className = "journal-entry";

    div.innerHTML = `
      <div class="time">${entry.time}</div>
      <div class="text">${entry.text}</div>
    `;

    list.appendChild(div);
  });
}

window.renderJournal = renderJournal;
