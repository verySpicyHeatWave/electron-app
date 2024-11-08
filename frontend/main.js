
const { app, BrowserWindow, dialog, ipcMain } = require('electron')
const path = require('node:path')

require('electron-reload')(__dirname)

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    alwaysOnTop:true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true
    }
  })

  mainWindow.loadFile('index.html')

  mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {
  createWindow()

  ipcMain.handle('dialog:saveFile', async () => {
    const { canceled, filePath } = await dialog.showSaveDialog()
    if (!canceled) {
      return filePath
    }
  })

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  });

});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
});