# Description: extract frames from previously recorded video.

# Include required libraries
from configurator import *
import cv2
import os
import shutil

# Return time interval of given frame according to given recording infos file
def get_frame_time_interval(rec_infos_file_path, frame_idx):
    rec_infos_file = open(rec_infos_file_path, 'r')
    rec_infos_file_lines = rec_infos_file.read().splitlines()
    rec_infos_file.close()

    rec_start, frame_rate = None, None
    for line in rec_infos_file_lines:
        line_infos = line.split('|')
        if line_infos[0] == 'rec_start':
            rec_start = int(line_infos[1])
        elif line_infos[0] == 'frame_rate':
            frame_rate = int(line_infos[1])

    frame_duration = 1000000000 / frame_rate # Duration of a frame in nanoseconds
    frame_start = rec_start + (frame_idx - 1) * frame_duration
    frame_end = rec_start + frame_idx * frame_duration

    return frame_start, frame_end

# Check if frame is relevant for next step of pipeline:
#   - A user event occured inside the monitor during the frame
def monitor_is_relevant(rec_infos_file_path, recording_id, frame_idx, monitor):
    frame_start, frame_end = get_frame_time_interval(rec_infos_file_path, frame_idx)

    mouse_rec_file_path = uploads_folder + recording_id + '_' + mouse_recording_file
    mouse_rec_file = open(mouse_rec_file_path, 'r')
    mouse_rec_file_lines = mouse_rec_file.read().splitlines()
    mouse_rec_file.close()

    for line in mouse_rec_file_lines:
        line_infos = line.split('|')

        evt_stamp = float(line_infos[0])
        if evt_stamp < frame_start:
            continue
        elif frame_end <= evt_stamp:
            break

        evt_x = int(line_infos[2])
        evt_y = int(line_infos[3])
        if monitor.x <= evt_x and evt_x < monitor.w and \
           monitor.y <= evt_y and evt_y < monitor.h:
            return True

    return False


# Extract monitor's image from frame and return count of monitors for frame
def extract_frame_monitors(recording_id, frame_folder, frame_idx, frame):
    rec_infos_file_path = uploads_folder + recording_id + '_' + recording_infos_file
    rec_infos_file = open(rec_infos_file_path, 'r')
    rec_infos_file_lines = rec_infos_file.read().splitlines()
    rec_infos_file.close()
    
    monitors_count = 0
    for i, line in enumerate(rec_infos_file_lines):
        line_infos = line.split('|')
        if line_infos[0] != 'monitor':
            continue

        x = int(line_infos[1]) # Monitor's horizontal position
        y = int(line_infos[2]) # Monitor's vertical position
        w = int(line_infos[3]) # Monitor's width
        h = int(line_infos[4]) # Monitor's height

        if monitor_is_relevant(rec_infos_file_path, recording_id, frame_idx, (x, y, w, h)):
            frame_path = frame_folder + '_' + str(i + 1) + '_' + str(frame_idx) + '.png'
            cv2.imwrite(frame_path, frame[y:(y + h), x:(x + w)])
            # Save .final file to inform worker that image file is fully created
            open(os.path.splitext(frame_path)[0] + '.final', 'x').close()
            monitors_count += 1 # Increment number of extracted frame's monitors

    return monitors_count

# Check if an event recorded in given events file occurs during given period
def event_is_occuring(events_file_path, start_time, end_time):
    event_file = open(events_file_path, 'r')
    event_file_lines = event_file.read().splitlines()
    event_file.close()
    for line in event_file_lines:
        evt_stamp = float(line.split('|')[0])
        if start_time <= evt_stamp and evt_stamp < end_time:
            return True
    return False

# Check if frame is relevant for next step of pipeline:
#   - A user event occured during the frame
def frame_is_relevant(rec_infos_file_path, recording_id, frame_idx):
    frame_start, frame_end = get_frame_time_interval(rec_infos_file_path, frame_idx)

    keyboard_rec_file_path = uploads_folder + recording_id + '_' + keyboard_recording_file
    keyboard_evt_is_occuring = os.path.isfile(keyboard_rec_file_path) and \
                               event_is_occuring(keyboard_rec_file_path, frame_start, frame_end)
    mouse_rec_file_path = uploads_folder + recording_id + '_' + mouse_recording_file
    mouse_evt_is_occuring = os.path.isfile(mouse_rec_file_path) and \
                            event_is_occuring(mouse_rec_file_path, frame_start, frame_end)

    return keyboard_evt_is_occuring or mouse_evt_is_occuring


# Extract frames from video
def extract_frames(video_name):
    cap = cv2.VideoCapture(uploads_folder + video_name)
    video_name = os.path.splitext(video_name)[0]
    recording_id = video_name.split('_')[0]
    rec_infos_file_path = uploads_folder + recording_id + '_' + recording_infos_file

    frame_idx = 1
    frames_images_count = 0
    detector_worker_idx = 1
    while cap.isOpened():
        ret, frame_img = cap.read()
        if not ret:
            break

        # Extract frame only if relevant
        if frame_is_relevant(rec_infos_file_path, recording_id, frame_idx):
            # Put frame image in a worker folder for next step of pipeline
            detector_worker_folder = frames_folder + 'worker' + str(detector_worker_idx) + '/'
            frame_folder = detector_worker_folder + video_name
            frames_images_count += extract_frame_monitors(recording_id, frame_folder, frame_idx, frame_img)

            detector_worker_idx = detector_worker_idx % detector_workers_count + 1

        frame_idx += 1

    rec_infos_file = open(rec_infos_file_path, 'a')
    rec_infos_file.write('frames_images_count|' + str(frames_images_count) + '\n')
    rec_infos_file.close()

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
        rec_db_folder = recordings_folder + recording_id + '/'
        if not os.path.exists(rec_db_folder):
            os.mkdir(rec_db_folder)
        rec_files = recording_files + [recording_infos_file]
        for rec_file in rec_files:
            extract_file(recording_id + '_' + rec_file, uploads_folder, rec_db_folder)

        # Delete .final file after storage into database and extraction
        os.remove(file_path)

        # Print completion of file extraction
        print('Extraction of recording ' + recording_id + ' completed')

# Program's main
if __name__ == '__main__':
    while True:
        extract()