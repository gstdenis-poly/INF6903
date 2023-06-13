// Description: record all screens of user in one .mp4 video.

// Include required librairies
const fs = require('fs');
const screenInfo = require('screen-info');
const recordScreen = require('record-screen'); // Require ffmpeg, x11grab
const ioHook = require('iohook'); // Require libxkbcommon-x11-0
const sleeper = require('sleep');

// Sleep for 1 second before starting to record
sleeper.sleep(1);

// Video recording
const res = screenInfo.main(); // Total resolution of all screens combined

const recording = recordScreen('./screen_recording.mp4', {
  resolution: res.width + 'x' + res.height, // Display resolution
  fps: 15 // Frame rate
});
recording.promise
  .then(result => {
    // Screen recording is done
    process.stdout.write(result.stdout);
    process.stderr.write(result.stderr);
  })
  .catch(err => console.error);

// Mouse events recording
const mouseRecPath = './mouse_recording.txt';
try {
  if (fs.existsSync(mouseRecPath))
    fs.unlinkSync(mouseRecPath); // Delete file if already exists
} catch (err) {
  console.log(err);
}
ioHook.on('mouseclick', (evt) => {
  var content = evt.button + ';' + evt.x + ';' + evt.y + '\n';
  fs.appendFile(mouseRecPath, content, err => console.error);
});

// Keyboard events recording and Quit on holding Esc key for at least 1 second
const kbRecPath = './keyboard_recording.txt';
try {
  if (fs.existsSync(kbRecPath))
    fs.unlinkSync(kbRecPath); // Delete file if already exists
} catch (err) {
  console.log(err);
}
var qDownDatetime = null;
var qDownDuration = 0;
var qKeyCode = 1;

ioHook.on('keydown', (evt) => {
  var altKey = evt.altKey ? 1 : 0;
  var ctrlKey = evt.ctrlKey ? 1 : 0;
  var shiftKey = evt.shiftKey ? 1 : 0;
  var content = evt.keycode + ';' + altKey + ';' + ctrlKey + ';' + shiftKey + '\n';

  if (evt.keycode != qKeyCode) { 
    fs.appendFile(kbRecPath, content, err => console.error); // Keyboard events recording
    return;
  }

  if (qDownDatetime == null) {
    fs.appendFile(kbRecPath, content, err => console.error); // Keyboard q key events recording
    qDownDatetime = new Date();
  } else
    qDownDuration = new Date() - qDownDatetime;

  if (qDownDuration < 1000 /*1 second*/)
    return;
  
  recording.stop();
  process.exit();
});
ioHook.on('keyup', (evt) => {
  if (evt.keycode != qKeyCode)
    return;

  qDownDatetime = null;
  qDownDuration = 0;
});
process.on('exit', () => { ioHook.unload(); });

// Register and start hook
ioHook.start();