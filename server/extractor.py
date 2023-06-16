# Description: extract frames from previously recorded video.

# Include required libraries
import cv2
import os
import shutil

uploads_folder = '/home/gstdenis/scratch/uploads/'
frames_folder = '/home/gstdenis/scratch/frames/'
database_folder = '/home/gstdenis/projects/def-gabilode/gstdenis/database/'
recording_files = [
    'mouse_recording.txt', 'keyboard_recording.txt', 'screen_recording.mp4'
    ]
detector_workers_count = 5

# Extract frames from video
def extract_frames(video_name):
    cap = cv2.VideoCapture(uploads_folder + video_name)

    video_name = os.path.splitext(video_name)[0]
    recording_id = video_name.split('_')[0]

    rec_frames_db_folder = database_folder + recording_id + '/frames/'
    if not os.path.exists(rec_frames_db_folder):
        os.mkdir(rec_frames_db_folder)

    frame_idx = 1
    worker_idx = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Put frame image in a worker folder for next step of pipeline
        worker_folder = frames_folder + 'worker' + str(worker_idx) + '/'
        frame_path = worker_folder + video_name + '_' + str(frame_idx) + '.png'
        cv2.imwrite(frame_path, frame)

        # Save frame to database
        shutil.copy(frame_path, rec_frames_db_folder)

        frame_idx += 1
        worker_idx = (worker_idx + 1) % detector_workers_count

    cap.release()
    cv2.destroyAllWindows()

# Extract recording files from uploads to database and extract frames if video
def extract_file(file_name, src_folder, dest_folder):
    file_path = src_folder + file_name
    if not os.path.isfile(file_path):
        return
    
    # Extract frames of video 
    if os.path.splitext(file_name)[1] == '.mp4':
        extract_frames(file_name)
    
    shutil.move(file_path, dest_folder)

    print('Extraction of file ' + file_name + ' completed')

# Program main function
def extract():
    for file_name in os.listdir(uploads_folder):
        file_path = uploads_folder + file_name
        if not os.path.isfile(file_path):
            continue

        # Skip iteration if not .final file
        file_name_parts = os.path.splitext(file_name)
        if file_name_parts[1] != '.final':
            continue

        # Save file into database
        recording_id = file_name_parts[0]
        rec_db_folder = database_folder + recording_id + '/'
        if not os.path.exists(rec_db_folder):
            os.mkdir(rec_db_folder)
        for rec_file in recording_files:
            extract_file(recording_id + '_' + rec_file, uploads_folder, rec_db_folder)

        # Delete .final file after storage into database and extraction
        os.remove(file_path)

        # Print completion of file extraction
        print('Extraction of recording ' + recording_id + ' completed')

# Program's main
if __name__ == '__main__':
    # Create detector worker folder for each detector server
    for i in range(detector_workers_count):
        detector_worker_folder = frames_folder + 'worker' + str(i + 1)
        if os.path.exists(detector_worker_folder):
            continue
            
        os.mkdir(detector_worker_folder)

    while True:
        extract()

