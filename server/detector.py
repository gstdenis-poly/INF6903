import os
from UIED_custom import run_single
import shutil

app_root = '.'
tmp_root = app_root + '/tmp'

while True:
  for folder in os.listdir(tmp_root):
    client_tmp = tmp_root + '/' + folder # tmp of specific client
    frames_path = client_tmp + '/uploads'

    if not os.path.exists(frames_path):
      continue

    frames = os.listdir(frames_path)

    for frame in frames:
      frame_name = os.path.splitext(frame)[0]
      frame_ext = os.path.splitext(frame)[-1]

      frame_path = frames_path + '/' + frame
      lock_file_path = frames_path + '/' + frame_name + '.lock'

      if os.path.exists(lock_file_path):
        continue
      elif frame_ext == '.png':
        lock_file = open(lock_file_path, 'w') # Create .lock file
        lock_file.close()

        output_root = app_root + '/database/' + folder + '/detections'
        run_single.run(frame_path, output_root)

        # Copy output into tmp folder for next step of pipeline
        client_tmp_detections = client_tmp + '/detections/'
        if not os.path.exists(client_tmp_detections):
          os.mkdir(client_tmp_detections)

        output_file_name = frame_name + '.json'
        shutil.copyfile(output_root + '/ocr/' + output_file_name,
                        client_tmp_detections + output_file_name)
        os.remove(frame_path) # Remove .png file
        os.remove(lock_file_path) # Remove .lock file
        break # Process one frame per client at each time