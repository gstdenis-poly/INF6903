# Description: record all screens of user in one .mp4 video and
#              record all mouse and keyboard events in text files.

# Include required librairies
from ffmpeg import FFmpeg # Require ffmpeg, x11grab
import os
from pynput import mouse, keyboard
from screeninfo import get_monitors
import time

# Keyboard events recording
def record_keyboard(mouse_listener, screen_recorder):
    keyboard_rec_file_path = './keyboard_recording.txt'
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
    mouse_rec_file_path = './mouse_recording.txt'
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
        .output('./screen_recording.mp4', vcodec = 'libx264', preset = 'veryslow')
    )
def record_screen(screen_recorder):
    @screen_recorder.on('terminated')
    def on_terminated():
        print('Recording succeed')
        exit()

    screen_recorder.execute()

# Start recording
time.sleep(1) # Sleep for 1 second before starting to record

mouse_listener = record_mouse()
screen_recorder = init_screen_recorder()
record_keyboard(mouse_listener, screen_recorder)
record_screen(screen_recorder)
