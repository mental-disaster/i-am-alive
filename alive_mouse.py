import time
import argparse
import threading
import configparser
from pynput.mouse import Controller

animation_list = {
    "spinner" : ["|", "/", "-", "\\"],
    "clock" : ["◴", "◷", "◶", "◵"],
    "ellipsis" : [".", "..", "..."],
    "pulsing" : [".", "o", "O", "o", "."],
    "bounce" : ["-", "--", "---", "----", "---", "--", "-"],
    "arrow" : ['>', '>>', '>>>']
}

def loading_animation(stop_event, rest_event, animation):
    idx = 0
    selected_animation = animation_list[animation]
    max_length = max(len(frame) for frame in selected_animation)

    while stop_event.is_set():
        status = "Working" if not rest_event.is_set() else 'Resting'
        frame = selected_animation[idx]
        print(f"\r{status} {frame}"+ " " * (max_length - len(frame)), end='', flush=True)
        idx = (idx + 1) % len(selected_animation)
        time.sleep(0.2)

def move_mouse(stop_event, rest_event, interval):
    mouse = Controller()
    interval = max(1, interval)

    while True:
        for _ in range(interval * 5):
            if not stop_event.is_set():
                return
            time.sleep(0.2)

        if not rest_event.is_set():
            mouse.move(1, 0)
            mouse.move(-1, 0)

def scheduler(stop_event, rest_event, break_start, break_end, work_end):
    break_start_hour_min = (break_start.tm_hour, break_start.tm_min) if break_start else ''
    break_end_hour_min = (break_end.tm_hour, break_end.tm_min) if break_end else ''
    work_end_hour_min = (work_end.tm_hour, work_end.tm_min) if work_end else ''

    while stop_event.is_set():
        current_time = time.localtime()
        current_hour_min = (current_time.tm_hour, current_time.tm_min)

        if work_end_hour_min and work_end_hour_min <= current_hour_min:
            stop_event.clear()
        elif break_start_hour_min and break_end_hour_min and break_start_hour_min <= current_hour_min <= break_end_hour_min:
            rest_event.set()
        else:
            rest_event.clear()
        time.sleep(0.2)

def stop_working(stop_event):
    input("Press Enter to stop the program...\n")
    stop_event.clear()

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--animation', help='Select working animation', default="spinner", choices=animation_list.keys())
    arg_parser.add_argument('--interval', help='Mouse moving interval in seconds', type=int, default=10)
    opt = arg_parser.parse_args()

    config = configparser.ConfigParser()
    config.read("config.ini")
    try:
        break_start = time.strptime(config["time"]["break_start"], "%H:%M")
    except ValueError:
        break_start = ''
    try:
        break_end = time.strptime(config["time"]["break_end"], "%H:%M")
    except ValueError:
        break_end = ''
    try:
        work_end = time.strptime(config["time"]["work_end"], "%H:%M")
    except ValueError:
        work_end = ''

    is_working = threading.Event()
    is_resting = threading.Event()
    is_working.set()

    activation_thread = threading.Thread(target=stop_working, args=(is_working,))
    timer_thread = threading.Thread(target=scheduler, args=(is_working, is_resting, break_start, break_end, work_end,))
    animation_thread = threading.Thread(target=loading_animation, args=(is_working, is_resting, opt.animation,))
    mouse_thread = threading.Thread(target=move_mouse, args=(is_working, is_resting, opt.interval,))

    activation_thread.start()
    timer_thread.start()
    animation_thread.start()
    mouse_thread.start()

    timer_thread.join()
    animation_thread.join()
    mouse_thread.join()
    
    print("Jobs done...")
