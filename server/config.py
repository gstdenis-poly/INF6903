# Description: global variables for server configurations.

# Folders
uploads_folder = '/home/gstdenis/scratch/uploads/'
frames_folder = '/home/gstdenis/scratch/frames/'
database_folder = '/home/gstdenis/projects/def-gabilode/gstdenis/database/'
detections_folder = '/home/gstdenis/scratch/detections/'
# Recording files' name
recording_files = [
    'mouse_recording.txt', 'keyboard_recording.txt', 'screen_recording.mp4'
    ]
# Number of workers
detector_workers_count = 100
clusterizer_workers_count = 50
# Index variables of workers
detector_worker_id = None
