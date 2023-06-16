import os
from UIED_custom import run_single
import shutil
import sys

frames_folder = '/home/gstdenis/scratch/frames/'
detections_folder = '/home/gstdenis/scratch/detections/'
database_folder = '/home/gstdenis/projects/def-gabilode/gstdenis/database/'
detector_worker_id = None
clusterizer_worker_count = 5

# Program main function
def detect():
    frames_worker_folder = frames_folder + 'worker' + detector_worker_id + '/'
    if not os.path.exists(frames_worker_folder):
        print('No existing folder for worker ' + detector_worker_id)
        return

    for frame_name in os.listdir(frames_worker_folder):
        frame_name_parts = os.path.splitext(frame_name)
        if frame_name_parts[1] != '.png':
            continue

        frame_path = frames_worker_folder + '/' + frame_name
        
        # UIED Detection
        run_single.run(frame_path, detections_folder)

        # Put detections result files in a worker folder for next step of pipeline
        """worker_idx = 1
        worker_folder = frames_folder + 'worker' + str(worker_idx) + '/'
        client_tmp_detections = client_tmp + '/detections/'
        if not os.path.exists(client_tmp_detections):
            os.mkdir(client_tmp_detections)

        output_file_name = frame_name_parts[0] + '.json'
        shutil.copyfile(output_root + '/ocr/' + output_file_name,
                        client_tmp_detections + output_file_name)"""
        
        os.remove(frame_path) # Remove .png file

# Program's main
if __name__ == '__main__':
    # Create clusterizer worker folder for each clusterizer server
    for i in range(clusterizer_worker_count):
        clusterizer_worker_folder = detections_folder + 'worker' + str(i + 1)
        if os.path.exists(clusterizer_worker_folder):
            continue
            
        os.mkdir(clusterizer_worker_folder)

    if len(sys.argv) != 2:
        print('Wrong arguments')
    else:
        detector_worker_id = sys.argv[1]
        while True:
            detect()