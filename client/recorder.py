# Description: record all screens of user in one .mp4 video and
#              record all mouse and keyboard events in text files.

# Include required librairies
from datetime import datetime
from ffmpeg import FFmpeg # Require ffmpeg, x11grab
import os
from pynput import mouse, keyboard
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

    def on_event(key, event):
        evt_stamp = datetime.timestamp(datetime.now())

        keyboard_rec_file = open(keyboard_rec_file_path, 'a')
        keyboard_rec_file.write(str(evt_stamp) + '|' + str(key) + '|' + event + '\n')
        keyboard_rec_file.close()

    def on_press(key):
        on_event(key, 'Press')

    def on_release(key):
        on_event(key, 'Release')

        if key == keyboard.Key.esc:
            mouse_listener.stop()
            screen_recorder.terminate()
            return False

    listener = keyboard.Listener(on_press = on_press, on_release = on_release)
    listener.start()

# Mouse events recording
def record_mouse():
    mouse_rec_file_path = './tmp/mouse_recording.txt'
    if os.path.isfile(mouse_rec_file_path):
        os.remove(mouse_rec_file_path)

    def on_click(x, y, button, pressed): # On click handler
        if pressed:
            evt_stamp = datetime.timestamp(datetime.now())

            mouse_rec_file = open(mouse_rec_file_path, 'a')
            mouse_rec_file.write(str(evt_stamp) + '|' + str(button) + '|' + str(x) + '|' + str(y) + '\n')
            mouse_rec_file.close()

    listener = mouse.Listener(on_click = on_click)
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
        recording_infos_file = open('./tmp/recording_infos.txt', 'a')
        recording_infos_file.write('rec_start|' + str(datetime.timestamp(datetime.now())) + '\n')
        recording_infos_file.write('frame_rate|15\n')
        recording_infos_file.close()

    @screen_recorder.on('terminated')
    def on_terminated():
        print('Recording completed')

    screen_recorder.execute()

# Upload recording on server
def upload_recording(ssh_address, ssh_pwd):
    rec_stamp = datetime.timestamp(datetime.now())
    scp_base_args = [
        'sshpass', '-p', ssh_pwd,
        'scp', '-o', 'StrictHostKeyChecking=no',
        '-l', '8192' # Limiting bandwidth to 1MB/s to avoid file transfer stalling
        ]

    for rec_name in os.listdir('./tmp'):
        scp_command = scp_base_args + [ 
            './tmp/' + rec_name,
            ssh_address + ':' + uploads_folder + str(rec_stamp) + '_' + rec_name
            ]
        subprocess.Popen(scp_command).wait()

    # Save .final file to inform server that upload is completed
    final_file_name = str(rec_stamp) + '.final'
    final_file_path = './tmp/' + final_file_name
    open(final_file_path, 'x')
    scp_command = scp_base_args + [
        final_file_path, 
        ssh_address + ':' + uploads_folder + final_file_name
    ]
    subprocess.Popen(scp_command).wait()

    print('Recording saved')

# Initialize recording's metadata
def init_recording_infos():
    recording_infos_file = open('./tmp/recording_infos.txt', 'w')
    for monitor in get_monitors():
        recording_infos_file.write('monitor|')
        recording_infos_file.write(str(monitor.x) + '|' + str(monitor.y) + '|' +
                                   str(monitor.width) + '|' + str(monitor.height) + '\n')
    recording_infos_file.close()

# Program main function
def record(ssh_address, ssh_pwd):
    tmp_dir_path = './tmp'
    if os.path.exists(tmp_dir_path):
        shutil.rmtree(tmp_dir_path)
    
    os.mkdir(tmp_dir_path)

    init_recording_infos()
    mouse_listener = record_mouse()
    screen_recorder = init_screen_recorder()
    record_keyboard(mouse_listener, screen_recorder)
    record_screen(screen_recorder)
    upload_recording(ssh_address, ssh_pwd)

    shutil.rmtree(tmp_dir_path)

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Wrong arguments')
    else:
        ssh_address = sys.argv[1]
        ssh_pwd = sys.argv[2]

        time.sleep(1) # Sleep for 1 second before starting to record
        record(ssh_address, ssh_pwd)
