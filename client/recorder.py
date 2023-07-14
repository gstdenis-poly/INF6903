# Description: record all screens of user in one .mp4 video and
#              record all mouse and keyboard events in text files.

# Include required librairies
import cv2
from ffmpeg import FFmpeg # Require ffmpeg, x11grab
import os
from pynput import mouse, keyboard
from pynput.keyboard import Key
from screeninfo import get_monitors
import shutil
import time

# Keyboard events recording
def record_keyboard(rec_folder, mouse_listener, screen_recorder):
    keyboard_rec_file_path = rec_folder + 'keyboard_recording.txt'
    if os.path.isfile(keyboard_rec_file_path):
        os.remove(keyboard_rec_file_path)

    def on_release(key):
        if key == Key.esc:
            mouse_listener.stop()
            screen_recorder.terminate()
            return False
        elif key not in [Key.enter, Key.tab, Key.left, Key.right, Key.up,
                         Key.down, Key.alt, Key.shift, Key.ctrl]:
            return True

        evt_stamp = time.time_ns()

        keyboard_rec_file = open(keyboard_rec_file_path, 'a')
        keyboard_rec_file.write(str(evt_stamp) + '|' + str(key) + '|Release\n')
        keyboard_rec_file.close()

    listener = keyboard.Listener(on_release = on_release)
    listener.start()

# Mouse events recording
def record_mouse(rec_folder):
    mouse_rec_file_path = rec_folder + 'mouse_recording.txt'
    if os.path.isfile(mouse_rec_file_path):
        os.remove(mouse_rec_file_path)

    def on_click(x, y, button, pressed): # On click handler
        if pressed:
            return

        evt_stamp = time.time_ns()

        mouse_rec_file = open(mouse_rec_file_path, 'a')
        mouse_rec_file.write(str(evt_stamp) + '|' + str(button) + '|' + str(x) + '|' + str(y) + '\n')
        mouse_rec_file.close()

    def on_scroll(x, y, dx, dy): # On scroll handler
        evt_stamp = time.time_ns()

        mouse_rec_file = open(mouse_rec_file_path, 'a')
        mouse_rec_file.write(str(evt_stamp) + '|Scroll|' + str(x) + '|' + str(y) + '\n')
        mouse_rec_file.close()

    listener = mouse.Listener(on_click = on_click, on_scroll = on_scroll)
    listener.start()

    return listener

# Screen video recording
def init_screen_recorder(rec_folder):
    monitors = get_monitors()
    last_monitor_x = sorted(monitors, key = lambda monitor: monitor.x)[-1]
    last_monitor_y = sorted(monitors, key = lambda monitor: monitor.y)[-1]
    res_x = last_monitor_x.x + last_monitor_x.width # Total X resolution
    res_y = last_monitor_y.y + last_monitor_y.height # Total Y resolution

    return (
        FFmpeg()
        .option('y')
        .input(':0', s = str(res_x) + 'x' + str(res_y), r = 15, f = 'x11grab')
        .output(rec_folder + 'screen_recording.mp4', vcodec = 'libx264', preset = 'ultrafast')
    )
def record_screen(rec_folder, screen_recorder):
    @screen_recorder.on('start')
    def on_start(arguments):
        print('Recording started')
        recording_infos_file = open(rec_folder + 'recording_infos.txt', 'a')
        recording_infos_file.write('rec_start|' + str(time.time_ns()) + '\n')
        recording_infos_file.write('frame_rate|15\n')
        recording_infos_file.close()

    @screen_recorder.on('terminated')
    def on_terminated():
        print('Recording completed')
        cap = cv2.VideoCapture(rec_folder + 'screen_recording.mp4')
        frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        recording_infos_file = open(rec_folder + 'recording_infos.txt', 'a')
        recording_infos_file.write('frames_count|' + str(frames_count) + '\n')
        recording_infos_file.close()

    screen_recorder.execute()

# Initialize recording's metadata
def init_recording_infos(rec_folder):
    recording_infos_file = open(rec_folder + 'recording_infos.txt', 'w')
    for monitor in get_monitors():
        recording_infos_file.write('monitor|')
        recording_infos_file.write(str(monitor.x) + '|' + str(monitor.y) + '|' +
                                   str(monitor.width) + '|' + str(monitor.height) + '\n')
    recording_infos_file.close()

# Program main function
def record():
    recordings_folder = './recordings/'
    recording_id = str(time.time_ns())
    rec_folder = recordings_folder + recording_id + '/'
    if not os.path.exists(recordings_folder):
        os.mkdir(recordings_folder)
    elif os.path.exists(rec_folder):
        shutil.rmtree(rec_folder)
    os.mkdir(rec_folder)

    init_recording_infos(rec_folder)
    mouse_listener = record_mouse(rec_folder)
    screen_recorder = init_screen_recorder(rec_folder)
    record_keyboard(rec_folder, mouse_listener, screen_recorder)
    record_screen(rec_folder, screen_recorder)
    shutil.make_archive(recordings_folder + recording_id, 'zip', rec_folder)

    shutil.rmtree(rec_folder)

# Program's main
if __name__ == '__main__':
    record()
