
const { app, BrowserWindow, dialog, ipcMain } = require('electron')
require('electron-reload')(__dirname)
const path = require('node:path')

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true
    }
  })

  mainWindow.loadFile('index.html')

  mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {
  ipcMain.handle('dialog:saveFile', handleFileSave)
  createWindow()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
});


async function handleFileSave () {
  const { canceled, filePath } = await dialog.showSaveDialog()
  if (!canceled) {
    return filePath
  }
}