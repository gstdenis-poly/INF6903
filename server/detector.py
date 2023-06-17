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
    detector_worker_ip_folder = detector_worker_folder + 'ip/'
    detector_worker_ocr_folder = detector_worker_folder + 'ocr/'

    if not os.path.exists(detector_worker_folder):
        return

    for frame_name in os.listdir(detector_worker_folder):
        frame_name_parts = os.path.splitext(frame_name)
        if frame_name_parts[1] != '.png' or not os.path.isfile(frame_name_parts[0] + '.final'):
            continue

        frame_path = detector_worker_folder + '/' + frame_name
        
        # UIED Detection
        run_single.run(frame_path, detector_worker_folder)

        # Put detections result files in a worker folder for next step of pipeline
        clusterizer_worker_idx = randint(1, clusterizer_workers_count)
        clusterizer_worker_folder = detections_folder + 'worker' + str(clusterizer_worker_idx) + '/'
        shutil.copytree(detector_worker_ip_folder, clusterizer_worker_folder + 'ip/', dirs_exist_ok = True)
        shutil.copytree(detector_worker_ocr_folder, clusterizer_worker_folder + 'ocr/', dirs_exist_ok = True)

        # Save detections to database
        """recording_id = frame_name.split('_')[0]
        rec_detections_db_folder = database_folder + recording_id + '/detections/'
        if not os.path.exists(rec_detections_db_folder):
            os.mkdir(rec_detections_db_folder)

        shutil.copytree(detector_worker_ip_folder, rec_detections_db_folder + 'ip/', dirs_exist_ok = True)
        shutil.copytree(detector_worker_ocr_folder, rec_detections_db_folder + 'ocr/', dirs_exist_ok = True)"""
        
        # Delete frame and its detection folders after copying for next worker and to database
        shutil.rmtree(detector_worker_ip_folder) # Remove ip folder
        shutil.rmtree(detector_worker_ocr_folder) # Remove ocr folder
        os.remove(frame_path) # Remove .png file

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Wrong arguments')
    else:
        detector_worker_id = sys.argv[1]
        while True:
            detect()