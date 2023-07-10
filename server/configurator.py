# Description: provide global variables for server configurations and
#              initialize server.

# Include required libraries
import os

# Folders
uploads_folder = '/home/gstdenis/scratch/uploads/'
frames_folder = '/home/gstdenis/scratch/frames/'
database_folder = '/home/gstdenis/projects/def-gabilode/gstdenis/database/'
recordings_folder = database_folder + 'recordings/'
accounts_folder = database_folder + 'accounts/'
results_folder = database_folder + 'results/'
res_clusters_folder = results_folder + 'clusters/'
res_detections_folder = results_folder + 'detections/'
res_tokens_folder = results_folder + 'tokens/'
validations_folder = database_folder + 'validations/'
val_clusters_folder = validations_folder + 'clusters/'
detections_folder = '/home/gstdenis/scratch/detections/'
clusters_folder = '/home/gstdenis/scratch/clusters/'
tokens_folder = '/home/gstdenis/scratch/tokens/'
corpus_folder = database_folder + 'corpus/'
# Recording files' name
mouse_recording_file = 'mouse_recording.txt'
keyboard_recording_file = 'keyboard_recording.txt'
screen_recording_file = 'screen_recording.mp4'
# Recording's metadata file
recording_infos_file = 'recording_infos.txt'
# Number of workers
detector_workers_count = 100
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