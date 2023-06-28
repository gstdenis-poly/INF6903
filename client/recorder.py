# Description: record all screens of user in one .mp4 video and
#              record all mouse and keyboard events in text files.

# Include required librairies
from authenticator import authenticate
import cv2
from ffmpeg import FFmpeg # Require ffmpeg, x11grab
import os
from pynput import mouse, keyboard
from pynput.keyboard import Key
from screeninfo import get_monitors
import shutil
import subprocess
import sys
import time

uploads_folder = '~/scratch/uploads/'

# Keyboard events recording
def record_keyboard(mouse_listener, screen_recorder):
    keyboard_rec_file_path = './tmp/keyboard_recording.txt'
    if os.path.isfile(keyboard_rec_file_path):
        os.remove(keyboard_rec_file_path)

    def on_release(key):
        if key == Key.esc:
            mouse_listener.stop()
            screen_recorder.terminate()
            return False
        elif key not in [Key.enter, Key.tab, Key.left, Key.right, Key.up, Key.down]:
            return True

        evt_stamp = time.time_ns()

        keyboard_rec_file = open(keyboard_rec_file_path, 'a')
        keyboard_rec_file.write(str(evt_stamp) + '|' + str(key) + '|Release\n')
        keyboard_rec_file.close()

    listener = keyboard.Listener(on_release = on_release)
    listener.start()

# Mouse events recording
def record_mouse():
    mouse_rec_file_path = './tmp/mouse_recording.txt'
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
def init_screen_recorder():
    monitors = get_monitors()
    last_monitor_x = sorted(monitors, key = lambda monitor: monitor.x)[-1]
    last_monitor_y = sorted(monitors, key = lambda monitor: monitor.y)[-1]
    res_x = last_monitor_x.x + last_monitor_x.width # Total X resolution
    res_y = last_monitor_y.y + last_monitor_y.height # Total Y resolution

    return (
        FFmpeg()
        .option('y')
        .input(':0', s = str(res_x) + 'x' + str(res_y), r = 15, f = 'x11grab')
        .output('./tmp/screen_recording.mp4', vcodec = 'libx264', preset = 'ultrafast')
    )
def record_screen(screen_recorder):
    @screen_recorder.on('start')
    def on_start(arguments):
        print('Recording started')
        recording_infos_file = open('./tmp/recording_infos.txt', 'a')
        recording_infos_file.write('rec_start|' + str(time.time_ns()) + '\n')
        recording_infos_file.write('frame_rate|15\n')
        recording_infos_file.close()

    @screen_recorder.on('terminated')
    def on_terminated():
        print('Recording completed')
        cap = cv2.VideoCapture("./tmp/screen_recording.mp4")
        frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        recording_infos_file = open('./tmp/recording_infos.txt', 'a')
        recording_infos_file.write('frames_count|' + str(frames_count) + '\n')
        recording_infos_file.close()

    screen_recorder.execute()

# Save video recording in a local recordings folder
def save_recording(recording_id):
    recordings_folder = './recordings/'
    if not os.path.exists(recordings_folder):
        os.mkdir(recordings_folder)

    tmp_rec_name = 'screen_recording.mp4'
    saved_rec_path = recordings_folder + recording_id + '_' + tmp_rec_name
    shutil.copyfile('./tmp/' + tmp_rec_name, saved_rec_path)

# Upload recording on server
def upload_recording(ssh_address, ssh_pwd, recording_id):
    scp_base_args = [
        'sshpass', '-p', ssh_pwd,
        'scp', '-o', 'StrictHostKeyChecking=no',
        '-l', '8192' # Limiting bandwidth to 1MB/s to avoid file transfer stalling
        ]

    for rec_name in os.listdir('./tmp'):
        scp_command = scp_base_args + [ 
            './tmp/' + rec_name,
            ssh_address + ':' + uploads_folder + recording_id + '_' + rec_name
            ]
        subprocess.Popen(scp_command).wait()

    # Save .final file to inform server that upload is completed
    final_file_name = recording_id + '.final'
    final_file_path = './tmp/' + final_file_name
    open(final_file_path, 'x').close()
    scp_command = scp_base_args + [
        final_file_path, 
        ssh_address + ':' + uploads_folder + final_file_name
    ]
    subprocess.Popen(scp_command).wait()

    print('Recording uploaded')

# Initialize recording's metadata
def init_recording_infos():
    recording_infos_file = open('./tmp/recording_infos.txt', 'w')
    for monitor in get_monitors():
        recording_infos_file.write('monitor|')
        recording_infos_file.write(str(monitor.x) + '|' + str(monitor.y) + '|' +
                                   str(monitor.width) + '|' + str(monitor.height) + '\n')
    recording_infos_file.close()

# Program main function
def record(ssh_address, ssh_pwd, acc_name):
    tmp_dir_path = './tmp'
    if os.path.exists(tmp_dir_path):
        shutil.rmtree(tmp_dir_path)
    
    os.mkdir(tmp_dir_path)

    init_recording_infos()
    mouse_listener = record_mouse()
    screen_recorder = init_screen_recorder()
    record_keyboard(mouse_listener, screen_recorder)
    record_screen(screen_recorder)

    rec_stamp = time.time_ns()
    recording_id = acc_name + '-' + str(rec_stamp)
    save_recording(recording_id)
    upload_recording(ssh_address, ssh_pwd, recording_id)

    shutil.rmtree(tmp_dir_path)

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Wrong arguments')
    else:
        ssh_address = sys.argv[1]
        ssh_pwd = sys.argv[2]

        # Start recording only if user can be authenticated
        acc_name = authenticate(ssh_address, ssh_pwd)
        if acc_name:
            record(ssh_address, ssh_pwd, acc_name)
