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
        const parsed = JSON.parse(line);
        
        // Handle data responses specially
        if (parsed.type === "data_response") {
          const dataType = parsed.data.type;
          const event = win._dataRequestEvent;
          if (event) {
            event.reply(`data-response-${dataType}`, parsed.data.data);
            win._dataRequestEvent = null;
          }
        }
        
        win.webContents.send("python-message", line);
      } catch (e) {
        console.log("Python stdout (raw):", line);
      }
    });
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error("Python stderr:", data.toString());
  });

  // Handle renderer messages to Python
  const { ipcMain } = require("electron");
  
  ipcMain.on("user-text", (event, text) => {
    console.log("User text received:", text);
    try {
      pythonProcess.stdin.write(JSON.stringify({ command: "text_input", data: text }) + "\n");
    } catch (e) {
      console.error("Error sending text to Python:", e);
    }
  });
  
  ipcMain.on("start-listening", (event) => {
    console.log("Start listening requested");
    try {
      pythonProcess.stdin.write(JSON.stringify({ command: "start_audio" }) + "\n");
    } catch (e) {
      console.error("Error sending start-listening to Python:", e);
    }
  });
  
  ipcMain.on("stop-listening", (event) => {
    console.log("Stop listening requested");
    try {
      pythonProcess.stdin.write(JSON.stringify({ command: "stop_audio" }) + "\n");
    } catch (e) {
      console.error("Error sending stop-listening to Python:", e);
    }
  });
  
  ipcMain.on("request-data", (event, dataType) => {
    console.log("Data request:", dataType);
    try {
      pythonProcess.stdin.write(JSON.stringify({ command: "get_data", data_type: dataType }) + "\n");
      // Store the event for later response
      win._dataRequestEvent = event;
    } catch (e) {
      console.error("Error requesting data from Python:", e);
    }
  });

  // Handle app exit
  win.on('closed', () => {
    // Send shutdown command
    try {
      pythonProcess.stdin.write(JSON.stringify({ command: "shutdown" }) + "\n");
    } catch (e) { }
    pythonProcess.kill();
  });

  // Do NOT auto-start the listener - wait for user to press mic button
  // Users will trigger recording via startListening() when they hold the mic button
  // setTimeout(() => {
  //   if (pythonProcess.stdin.writable) {
  //     pythonProcess.stdin.write(JSON.stringify({ command: "start" }) + "\n");
  //   }
  // }, 2000);

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
