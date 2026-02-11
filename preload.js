const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("vaani", {
  onPythonMessage: (callback) =>
    ipcRenderer.on("python-message", (_, data) => callback(data)),
  
  sendUserText: (text) => {
    ipcRenderer.send("user-text", text);
  },
  
  startListening: () => {
    ipcRenderer.send("start-listening");
  },
  
  stopListening: () => {
    ipcRenderer.send("stop-listening");
  },
  
  requestData: (dataType) => {
    return new Promise((resolve) => {
      const channel = `data-response-${dataType}`;
      ipcRenderer.once(channel, (_, data) => {
        resolve(data);
      });
      ipcRenderer.send("request-data", dataType);
    });  }
});