const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");


function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 720,
    backgroundColor: "#cfdced",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile(path.join(__dirname, "ui", "index.html"));

const pythonProcess = spawn("py", ["-3.11", "main.py"], {
  cwd: __dirname
});

console.log("Python spawn attempted with py -3.11");

pythonProcess.stdout.on("data", (data) => {
  win.webContents.send("python-message", data.toString());
});

pythonProcess.stderr.on("data", (data) => {
  console.error("Python error:", data.toString());
});

}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
