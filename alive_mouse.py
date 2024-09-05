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

def loading_animation(stop_event, animation="spinner"):
    idx = 0
    selected_animation = animation_list[animation]
    max_length = max(len(frame) for frame in selected_animation)

    while stop_event.is_set():
        frame = selected_animation[idx]
        print(f"\rWorking {frame}", end='', flush=True)
        idx = (idx + 1) % len(selected_animation)
        time.sleep(0.2)

def move_mouse(stop_event, interval):
    mouse = Controller()
    tick = 4

    while stop_event.is_set():
        mouse.move(1, 0)
        mouse.move(-1, 0)

        for _ in range(interval*tick):
            if not stop_event.is_set():
                return
            time.sleep(1/tick)

def stop_working(stop_event):
    input("Press Enter to stop the program...\n")
    stop_event.clear()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--animation', help='Select working animation', default="spinner", choices=animation_list.keys())
    parser.add_argument('--interval', help='Mouse moving interval in seconds', type=int, default=10)
    opt = parser.parse_args()

    is_working = threading.Event()
    is_working.set()

    activation_thread = threading.Thread(target=stop_working, args=(is_working,))
    animation_thread = threading.Thread(target=loading_animation, args=(is_working, opt.animation,))
    mouse_thread = threading.Thread(target=move_mouse, args=(is_working, opt.interval,))

    activation_thread.start()
    animation_thread.start()
    mouse_thread.start()

    activation_thread.join()
    animation_thread.join()
    mouse_thread.join()
    
    print("Jobs done...")
