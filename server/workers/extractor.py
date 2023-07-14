# Description: extract frames from previously recorded video.

# Include required libraries
from configurator import *
import cv2
import math
import os
import random
import shutil
from web.models import Account, KeyboardEvent, Monitor, MouseEvent, Recording

# Update global statistics for given recording
def update_statistics(recording_id):
    # Number and distance of mouse events
    mouse_events_count, mouse_events_distance = 0, 0.0
    prev_evt_x, prev_evt_y = None, None
    for mouse_evt in MouseEvent.objects.all():
        mouse_events_count += 1
        evt_x, evt_y = mouse_evt.x, mouse_evt.y
        if not (prev_evt_x is None or prev_evt_y is None):
            mouse_events_distance += math.sqrt(math.pow(evt_x - prev_evt_x, 2) + math.pow(evt_y - prev_evt_y, 2))
        prev_evt_x, prev_evt_y = evt_x, evt_y
    # Number of keyboard events
    keyboard_events_count = len(KeyboardEvent.objects.all())
    # Save statistics
    recording = Recording.objects.get(id = recording_id)
    if recording != None:
        recording.mouse_events_count = mouse_events_count
        recording.keyboard_events_count = keyboard_events_count
        recording.mouse_events_distance = mouse_events_distance
        recording.save()

# Return time interval of given frame according to given recording infos file
def get_frame_time_interval(recording, frame_idx):
    frame_duration = 1000000000 / recording.frame_rate # Duration of a frame in nanoseconds
    frame_start = recording.rec_start + (frame_idx - 1) * frame_duration
    frame_end = recording.rec_start + frame_idx * frame_duration

    return frame_start, frame_end

# Check if given event (x, y) occurs inside given monitor (x1, y1, x2, y2)
def event_occurs_inside_monitor(event, monitor):
    return (monitor.x <= event.x and event.x < (monitor.x + monitor.width) and \
            monitor.y <= event.y and event.y < (monitor.y + monitor.height))

# Check if frame is relevant for next step of pipeline:
#   - A mouse event occured inside the monitor during the frame
#   - The last mouse event before the frame was inside the monitor
def monitor_is_relevant(recording, frame_idx, monitor):
    mouse_events = recording.mouse_events.all()
    if not mouse_events:
        return True
    
    frame_start, frame_end = get_frame_time_interval(recording, frame_idx)

    for event in sorted(mouse_events, key = lambda e: e.stamp, reverse = True):
        if frame_end <= event.stamp: # Event is after frame
            continue
        
        if event.stamp >= frame_start: # Event is during frame
            if event_occurs_inside_monitor(event, monitor):
                return True
        else: # Event is before frame
            return event_occurs_inside_monitor(event, monitor)           

    return False

# Extract monitor's image from frame and return count of monitors for frame
def extract_frame_monitors(recording, frame_folder, frame_idx, frame):
    monitors_count = 0
    for i, m in recording.monitors.all():
        if not monitor_is_relevant(recording, frame_idx, m):
            continue

        frame_path = frame_folder + '_' + str(i + 1) + '_' + str(frame_idx) + '.png'
        cv2.imwrite(frame_path, frame[m.y:(m.y + m.h), m.x:(m.x + m.w)])
        # Save .final file to inform worker that image file is fully created
        open(os.path.splitext(frame_path)[0] + '.final', 'w').close()
        monitors_count += 1 # Increment number of extracted frame's monitors

    return monitors_count

# Check if an event recorded in given events file occurs during given period
def event_is_occuring(events, start_time, end_time):
    for evt in events:
        if start_time <= evt.stamp and evt.stamp < end_time:
            return True
    return False

# Check if frame is relevant for next step of pipeline:
#   - A user event occured during the frame
def frame_is_relevant(recording, frame_idx):
    frame_start, frame_end = get_frame_time_interval(recording, frame_idx)

    keyboard_events = recording.keyboard_events.all()    
    keyboard_evt_is_occuring = keyboard_events and \
                               event_is_occuring(keyboard_events, frame_start, frame_end)
    mouse_events = recording.mouse_events.all()
    mouse_evt_is_occuring = mouse_events and \
                            event_is_occuring(mouse_events, frame_start, frame_end)

    return keyboard_evt_is_occuring or mouse_evt_is_occuring

# Extract frames from video
def extract_frames(video_name):
    recording_id = video_name.split('_')[0]
    cap = cv2.VideoCapture(recordings_folder + video_name)
    video_name = os.path.splitext(video_name)[0]
    recording = Recording.objects.get(id = recording_id)

    frame_idx = 1
    frames_images_count = 0
    while cap.isOpened():
        ret, frame_img = cap.read()
        if not ret:
            break

        # Extract frame only if relevant
        if frame_is_relevant(recording, frame_idx):
            detector_worker_idx = random.randint(1, detector_workers_count)
            # Put frame image in a worker folder for next step of pipeline
            detector_worker_folder = frames_folder + 'worker' + str(detector_worker_idx) + '/'
            frame_folder = detector_worker_folder + video_name
            frames_images_count += extract_frame_monitors(recording, frame_folder, frame_idx, frame_img)

        frame_idx += 1

    recording.frames_images_count = frames_images_count
    recording.save()

    cap.release()
    cv2.destroyAllWindows()

def extract_mouse_evt_file(recording_id, file_path):
    if not os.path.isfile(file_path):
        return

    mouse_evt_file = open(file_path, 'r')
    mouse_events = mouse_evt_file.read().splitlines()
    mouse_evt_file.close()

    for evt in mouse_events:
        evt_infos = evt.split('|')
        MouseEvent(recording_id = recording_id,
                   stamp = evt_infos[0],
                   button = evt_infos[1],
                   x = evt_infos[2],
                   y = evt_infos[3]).save()

    os.remove(file_path) # Delete file
    
    print('Extraction of file ' + mouse_recording_file + ' completed')

def extract_keyboard_evt_file(recording_id, file_path):
    if not os.path.isfile(file_path):
        return

    keyboard_evt_file = open(file_path, 'r')
    keyboard_events = keyboard_evt_file.read().splitlines()
    keyboard_evt_file.close()

    for evt in keyboard_events:
        evt_infos = evt.split('|')
        KeyboardEvent(recording_id = recording_id,
                      stamp = evt_infos[0],
                      key = evt_infos[1]).save()

    os.remove(file_path) # Delete file

    print('Extraction of file ' + keyboard_recording_file + ' completed')

def extract_rec_infos_file(recording_id, file_path):
    if not os.path.isfile(file_path):
        return

    rec_infos_file = open(file_path, 'r')
    rec_infos = rec_infos_file.read().splitlines()
    rec_infos_file.close()

    account = Account(username = recording_id.split('-')[0])
    recording = Recording(id = recording_id, account = account)
    for info in rec_infos:
        info_parts = info.split('|')
        if info_parts[0] == 'monitor':
            continue # Monitors must be saved after Recordings

        setattr(recording, info_parts[0], info_parts[1])
    recording.save()

    for info in rec_infos: 
        info_parts = info.split('|')
        if info_parts[0] != 'monitor':
            continue

        Monitor(recording_id = recording_id,
                x = info_parts[1],
                y = info_parts[2],
                width = info_parts[3],
                height = info_parts[4]).save()

    os.remove(file_path) # Delete file

    print('Extraction of file ' + recording_infos_file + ' completed')

def extract_screen_rec_file(recording_id, file_path):
    if not os.path.isfile(file_path):
        return
    
     # Save video file in database and extract its frames
    video_name = recording_id + '.mp4'
    shutil.move(file_path, recordings_folder + video_name)
    extract_frames(video_name)

    print('Extraction of file ' + screen_recording_file + ' completed')

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

        recording_id = file_name_parts[0]
        rec_upload_folder = uploads_folder + recording_id + '/'

        # Save file into database
        extract_rec_infos_file(recording_id, rec_upload_folder + recording_infos_file)
        extract_mouse_evt_file(recording_id, rec_upload_folder + mouse_recording_file)
        extract_keyboard_evt_file(recording_id, rec_upload_folder + keyboard_recording_file)
        extract_screen_rec_file(recording_id, rec_upload_folder + screen_recording_file)

        update_statistics(recording_id) # Update statistics of recording

        # Delete .final file and rec folder after extraction
        os.remove(file_path)
        shutil.rmtree(rec_upload_folder)

        # Print completion of file extraction
        print('Extraction of recording ' + recording_id + ' completed')

# Program's main
if __name__ == '__main__':
    while True:
        extract()