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

# Keyboard events recording
def record_keyboard(mouse_listener, screen_recorder):
    keyboard_rec_file_path = './tmp/keyboard_recording.txt'
    if os.path.isfile(keyboard_rec_file_path):
        os.remove(keyboard_rec_file_path)

    def on_event(key, event):
        keyboard_rec_file = open(keyboard_rec_file_path, 'a')
        keyboard_rec_file.write(str(key) + ';' + event + '\n')
        keyboard_rec_file.close()

    def on_press(key):
        on_event(key, 'Press')

    def on_release(key):
        on_event(key, 'Release')

        if str(key) == '\'q\'':
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
            mouse_rec_file = open(mouse_rec_file_path, 'a')
            mouse_rec_file.write(str(button) + ';' + str(x) + ';' + str(y) + '\n')
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
    @screen_recorder.on('terminated')
    def on_terminated():
        print('Recording completed')

    screen_recorder.execute()

# Save recording on server
def save_recording(ssh_user, ssh_pwd):
    now = datetime.now()
    rec_stamp = datetime.timestamp(now)

    for rec_path in os.listdir('./tmp'):
        scp_args = [
            'sshpass', 
            '-p', ssh_pwd, 
            'scp', '-o', 'StrictHostKeyChecking=no', 
            './tmp/' + rec_path, 
            ssh_user + '@cedar.calculcanada.ca:~/scratch/' + str(rec_stamp) + '_' + rec_path
            ]

        sp = subprocess.Popen(scp_args)
        sp.wait()

    print('Recording saved')

# Program main function
def record(ssh_user, ssh_pwd):
    tmp_dir_path = './tmp'
    if os.path.exists(tmp_dir_path):
        shutil.rmtree(tmp_dir_path)
    
    os.mkdir(tmp_dir_path)

    mouse_listener = record_mouse()
    screen_recorder = init_screen_recorder()
    record_keyboard(mouse_listener, screen_recorder)
    record_screen(screen_recorder)
    
    save_recording(ssh_user, ssh_pwd)

    shutil.rmtree(tmp_dir_path)

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Wrong arguments')
    else:
        ssh_user = sys.argv[1]
        ssh_pwd = sys.argv[2]

        time.sleep(1) # Sleep for 1 second before starting to record
        record(ssh_user, ssh_pwd)
