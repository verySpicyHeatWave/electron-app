
const { app, BrowserWindow, dialog, ipcMain } = require('electron')
const path = require('node:path')

require('electron-reload')(__dirname)

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    // width: 800,
    width: 1500,
    height: 600,
    // alwaysOnTop:true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true
    }
  })

  mainWindow.loadFile('index.html')

  mainWindow.webContents.openDevTools()
  return mainWindow;
}

app.whenReady().then(() => {
  const mainWindow = createWindow()

  ipcMain.handle('dialog:saveFile', async () => {
    const { canceled, filePath } = await dialog.showSaveDialog()
    if (!canceled) {
      return filePath
    }
  })

  ipcMain.on('dialog:requestStreamName', async () => {
    const inputBox = new BrowserWindow({
      width: 500,
      height: 300,
      alwaysOnTop: true,
      webPreferences: {
        preload: path.join(__dirname, 'inputBoxPreload.js'),
        nodeIntegration: true
      }
    });

    inputBox.loadFile('inputBox.html')
    inputBox.title = "Enter the RabbitMQ exchange:"
  })

  ipcMain.on("inputBox:resp", (event, exchange) => {
    console.log(exchange);
    mainWindow.webContents.send("exchange-name", exchange);
  })

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  });

});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
});