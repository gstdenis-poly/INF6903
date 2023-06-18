# Description: provide global variables for server configurations and
#              initialize server.

# Include required libraries
import os

# Folders
uploads_folder = '/home/gstdenis/scratch/uploads/'
frames_folder = '/home/gstdenis/scratch/frames/'
database_folder = '/home/gstdenis/projects/def-gabilode/gstdenis/database/'
detections_folder = '/home/gstdenis/scratch/detections/'
# Recording files' name
recording_files = [
    'mouse_recording.txt', 'keyboard_recording.txt', 'screen_recording.mp4'
    ]
# Recording's metadata file
recording_infos_file = 'recording_infos.txt'
# Number of workers
detector_workers_count = 100
clusterizer_workers_count = 50
# Index variables of workers
detector_worker_id = None

# Program's main
if __name__ == '__main__':
    # Create detector worker folder for each detector server
    for i in range(detector_workers_count):
        detector_worker_folder = frames_folder + 'worker' + str(i + 1)
        if os.path.exists(detector_worker_folder):
            continue
            
        os.mkdir(detector_worker_folder)

    # Create clusterizer worker folder for each clusterizer server
    for i in range(clusterizer_workers_count):
        clusterizer_worker_folder = detections_folder + 'worker' + str(i + 1)
        if os.path.exists(clusterizer_worker_folder):
            continue
            
        os.mkdir(clusterizer_worker_folder)
        os.mkdir(clusterizer_worker_folder + '/ip')
        os.mkdir(clusterizer_worker_folder + '/ocr')