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

  // Check if we are in dev or prod (packaged)
  // Logic: Try venv first, then fallback to system python
  let pythonCmd = "python";
  let pythonArgs = ["main.py"];

  const venvPython = process.platform === "win32"
    ? path.join(__dirname, "venv", "Scripts", "python.exe")
    : path.join(__dirname, "venv", "bin", "python");

  const fs = require('fs');
  if (fs.existsSync(venvPython)) {
    pythonCmd = venvPython;
  } else if (process.platform === "win32") {
    // Fallback: try just 'python' (which might be venv if opened from term) or 'py'
    pythonCmd = "python";
  } else {
    pythonCmd = "python3";
  }

  console.log(`Spawning python: ${pythonCmd} ${pythonArgs.join(" ")}`);

  const pythonProcess = spawn(pythonCmd, pythonArgs, {
    cwd: __dirname,
    stdio: ['pipe', 'pipe', 'pipe']
  });

  let buffer = "";

  pythonProcess.stdout.on("data", (data) => {
    buffer += data.toString();
    const lines = buffer.split("\n");
    buffer = lines.pop(); // Keep incomplete line

    lines.forEach(line => {
      if (!line.trim()) return;
      try {
        // Just forward the raw JSON string to renderer
        // validation happens in renderer or here if needed
        JSON.parse(line); // simple check
        win.webContents.send("python-message", line);
      } catch (e) {
        console.log("Python stdout (raw):", line);
      }
    });
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error("Python stderr:", data.toString());
  });

  // Handle app exit
  win.on('closed', () => {
    // Send stop command just in case
    try {
      pythonProcess.stdin.write(JSON.stringify({ command: "stop" }) + "\n");
    } catch (e) { }
    pythonProcess.kill();
  });

  // Start the assistant loop
  // Give it a moment to initialize
  setTimeout(() => {
    if (pythonProcess.stdin.writable) {
      pythonProcess.stdin.write(JSON.stringify({ command: "start" }) + "\n");
    }
  }, 2000);

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
