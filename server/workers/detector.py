# Description: detect GUI components and texts from videos' frames.

# Include required libraries
from configurator import *
import os
from random import randint
import shutil
import sys
from UIED_custom import run_single

# Program main function
def detect():
    detector_worker_folder = frames_folder + 'worker' + detector_worker_id + '/'
    detector_worker_ocr_folder = detector_worker_folder + 'ocr/'

    if not os.path.exists(detector_worker_folder):
        return

    for frame_name in os.listdir(detector_worker_folder):
        frame_name_parts = os.path.splitext(frame_name)
        if frame_name_parts[1] != '.png':
            continue

        frame_path = detector_worker_folder + frame_name
        if not os.path.isfile(os.path.splitext(frame_path)[0] + '.final'):
            continue
        
        # UIED Detection
        run_single.run(frame_path, detector_worker_folder)

        # Put detections result files in a folder for next step of pipeline
        shutil.copytree(detector_worker_ocr_folder, detections_folder, dirs_exist_ok = True)
        # Save .final file to inform worker that detection is fully completed
        open(detections_folder + frame_name_parts[0] + '.final', 'w').close()
        
        # Delete frame and its detection folders after copying for next step and to database
        shutil.rmtree(detector_worker_ocr_folder) # Remove ocr folder
        os.remove(frame_path) # Remove .png file
        os.remove(detector_worker_folder + frame_name_parts[0] + '.final') # Remove .final file

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Wrong arguments')
    else:
        detector_worker_id = sys.argv[1]
        while True:
            detect()