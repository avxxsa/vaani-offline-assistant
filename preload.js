const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("vaani", {
  onPythonMessage: (callback) =>
    ipcRenderer.on("python-message", (_, data) => callback(data))
});
