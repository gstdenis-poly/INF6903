# Description: extract frames from previously recorded video.

# Include required libraries
import cv2
import os
import shutil
import sys

uploads_folder = '~/scratch/uploads/'
frames_folder = '~/scratch/frames/'
database_folder = '~/projects/def-gabilode/gstdenis/INF6903/database/'

# Extract frames from video
def extract_frames(video_path, workers_count):
    cap = cv2.VideoCapture(uploads_folder + video_path)

    video_name = os.path.splitext(video_path)[0]

    frame_idx = 1
    worker_idx = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Put frame image in a worker folder
        worker_folder = frames_folder + worker_idx + '/'
        cv2.imwrite(worker_folder + video_name + '_' + str(frame_idx) + '.png', frame)

        frame_idx += 1
        worker_idx = (worker_idx + 1) % workers_count

    cap.release()
    cv2.destroyAllWindows()

# Program main function
def extract(workers_count):
    for file_path in os.listdir(uploads_folder):
        if not os.path.isfile(file_path):
            continue

        # Save file into database
        recording_id = file_path.split('_')[0]
        rec_db_folder = database_folder + recording_id + '/'
        if not os.path.exists(database_folder):
            os.mkdir(database_folder)
        shutil.copyfile(uploads_folder + file_path, rec_db_folder + file_path)

        # Create frames worker folder for each detector server
        for i in range(workers_count):
            frames_worker_folder = frames_folder + 'worker' + (i + 1)
            if os.path.exists(frames_worker_folder):
                continue
                
            os.mkdir(frames_worker_folder)

        # Extract frames of video 
        file_ext = os.path.splitext(file_path)[1]
        if file_ext == '.mp4':
            extract_frames(file_path, workers_count)

        # Delete file after save into database and extraction
        os.remove(uploads_folder + file_path)

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Wrong arguments')
    else:
        workers_count = sys.argv[1]
        while True:
            extract(workers_count)

