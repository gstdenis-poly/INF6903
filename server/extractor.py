# Description: extract frames from previously recorded video.

# Include required libraries
import cv2
import os
import shutil
import sys

uploads_folder = '/home/gstdenis/scratch/uploads/'
frames_folder = '/home/gstdenis/scratch/frames/'
database_folder = '/home/gstdenis/projects/def-gabilode/gstdenis/INF6903/database/'

# Extract frames from video
def extract_frames(video_name, workers_count):
    cap = cv2.VideoCapture(uploads_folder + video_name)

    video_name = os.path.splitext(video_name)[0]

    frame_idx = 1
    worker_idx = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Put frame image in a worker folder
        worker_folder = frames_folder + str(worker_idx) + '/'
        cv2.imwrite(worker_folder + video_name + '_' + str(frame_idx) + '.png', frame)

        frame_idx += 1
        worker_idx = (worker_idx + 1) % workers_count

    cap.release()
    cv2.destroyAllWindows()

# Program main function
def extract(workers_count):
    for file_name in os.listdir(uploads_folder):
        file_path = uploads_folder + file_name
        if not os.path.isfile(file_path):
            continue

        # Save file into database
        recording_id = file_name.split('_')[0]
        rec_db_folder = database_folder + recording_id + '/'
        if not os.path.exists(rec_db_folder):
            os.mkdir(rec_db_folder)
        shutil.copyfile(file_path, rec_db_folder + file_name)

        # Create frames worker folder for each detector server
        for i in range(workers_count):
            frames_worker_folder = frames_folder + 'worker' + str(i + 1)
            if os.path.exists(frames_worker_folder):
                continue
                
            os.mkdir(frames_worker_folder)

        # Extract frames of video 
        file_ext = os.path.splitext(file_name)[1]
        if file_ext == '.mp4':
            extract_frames(file_name, workers_count)

        # Delete file after save into database and extraction
        os.remove(file_path)

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Wrong arguments')
    else:
        workers_count = int(sys.argv[1])
        while True:
            extract(workers_count)

