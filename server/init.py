# Description: server initialization (must be run before any other task).

# Include required libraries
from config import *
import os

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
