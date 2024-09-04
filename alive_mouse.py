import sys
import time
import argparse
from pynput.mouse import Controller
import threading

animation_list = {
    "spinner" : ["|", "/", "-", "\\"],
    "clock" : ["◴", "◷", "◶", "◵"],
    "ellipsis" : [".", "..", "..."],
    "pulsing" : [".", "o", "O", "o", "."],
    "bounce" : ["-", "--", "---", "----", "---", "--", "-"],
    "arrow" : ['>', '>>', '>>>']
}

mouse = Controller()

is_working = True

def loading_animation(animation="Spinner"):
    idx = 0
    selected_animation = animation_list[animation]
    max_length = max(len(frame) for frame in selected_animation)

    while is_working:
        frame = selected_animation[idx]
        sys.stdout.write("\rWorking " + frame + " " * (max_length - len(frame)))
        sys.stdout.flush()
        idx = (idx + 1) % len(selected_animation)
        time.sleep(0.2)

def move_mouse():
    while is_working:
        mouse.move(1, 0)
        time.sleep(1)
        mouse.move(-1, 0)

def stop_working():
    global is_working
    input("Press Enter to stop the program...\n")
    is_working = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--animation', help='Select working animation')
    opt = parser.parse_args()

    animation = str(opt.animation).lower()
    if not(animation and animation in animation_list.keys()):
        animation = "spinner"

    activation_thread = threading.Thread(target=stop_working)
    animation_thread = threading.Thread(target=loading_animation, args=(animation,))
    mouse_thread = threading.Thread(target=move_mouse)
    activation_thread.start()
    animation_thread.start()
    mouse_thread.start()

    activation_thread.join()
    animation_thread.join()
    mouse_thread.join()
        
    print("프로그램 종료")
