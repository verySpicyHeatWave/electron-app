const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('resp', {
  sendToMain: (value) => {
    ipcRenderer.send("inputBox:resp", value)
  }
});