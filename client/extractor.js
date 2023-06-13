// Description: extract frames from previously recorded video
//              and upload each one on gdrive server.

// Include required libraries
const fs = require('fs');
const path = require('path');
const extractFrames = require('ffmpeg-extract-frames');
const { google } = require('googleapis');
const rimraf = require('rimraf');

// Initialize key file path and folder id
const dirFiles = fs.readdirSync(__dirname);
const keyFile = dirFiles.filter((file) => {
  const parsedFile = path.parse(file);
  return (parsedFile.name.substring(0, 7) === 'inf6909' && 
          parsedFile.ext === '.json');
})[0];
const keyFilePath = path.join(__dirname, keyFile);
const keyFileContent = fs.readFileSync(keyFilePath);
const folderId = JSON.parse(keyFileContent).folder_id;

// Starting Google Drive Service
const getDriveService = () => {
  const scopes = ['https://www.googleapis.com/auth/drive'];

  const auth = new google.auth.GoogleAuth({
    keyFile: keyFilePath,
    scopes: scopes,
  });
  const driveService = google.drive({ version: 'v3', auth });
  return driveService;
};

// Function for uploading file(s) to Google Drive
const drive = getDriveService();
const uploadSingleFile = async (fileName, filePath) => {
  const { data: { id, name } = {} } = await drive.files.create({
    resource: {
      name: fileName,
      parents: [folderId],
    },
    media: {
      mimeType: 'application/png',
      body: fs.createReadStream(filePath),
    },
    fields: 'id,name',
  });
  console.log('File Uploaded', name, id);
};
const scanFolderForFiles = async (folderPath) => {
  const folder = await fs.promises.readdir(folderPath);
  for await (const file of folder)
    await uploadSingleFile(file, path.join(folderPath, file));
};

// Extract frames from video in input and upload each frame to Google Drive
const inputPath = (process.argv.length > 2) ? process.argv[2] : './screen_recording.mp4';
const inputExt = path.extname(inputPath);
const inputName = path.basename(inputPath, inputExt);

const outputRoot = './' + path.parse(inputPath).name;
try {
  if (!fs.existsSync(inputPath))
    process.exit(1);
  else if (fs.existsSync(outputRoot)) 
    rimraf.sync(outputRoot); // Delete folder if already exists

  fs.mkdirSync(outputRoot); // Recreate empty folder
} catch (err) {
  console.log(err);
}
async function extract(){
  await extractFrames({
    input: inputPath, output: outputRoot + '/' + inputName + '-%d.png'
    })
    .then(() => { 
      // Upload of frames to Google Drive then remove folder of frames
      scanFolderForFiles(outputRoot).then(() => {
        console.log('All files have been uploaded to Google Drive successfully!');
        console.log('You will be notified when all files have been processed by server.')
        rimraf.sync(outputRoot);
      });
    })
    .catch((err) => console.error);
};
extract();