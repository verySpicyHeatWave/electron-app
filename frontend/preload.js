const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('dialogAPI', {
  saveFile: () => ipcRenderer.invoke('dialog:saveFile'),
  requestStreamName: () => ipcRenderer.send('dialog:requestStreamName'),
  onExchangeRequest: (callback) => ipcRenderer.on("exchange-name", (_event, value) => callback(value))
});