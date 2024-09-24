import time
import platform
import threading
import subprocess
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

CYCLE = 0.25

def loading_animation(working_event, rest_event, animation):
    idx = 0
    selected_animation = animation_list[animation]
    max_length = max(len(frame) for frame in selected_animation)

    while working_event.is_set():
        status = "Working" if not rest_event.is_set() else 'Resting'
        frame = selected_animation[idx]
        print(f"\r{status} {frame}"+ " " * (max_length - len(frame)), end='', flush=True)
        idx = (idx + 1) % len(selected_animation)
        time.sleep(CYCLE)

def move_mouse(working_event, rest_event, interval):
    mouse = Controller()
    interval = max(1, interval)
    cycle_count = 0

    while working_event.is_set():
        if not rest_event.is_set() and cycle_count >= interval:
            cycle_count = 0
            mouse.move(1, 0)
            mouse.move(-1, 0)

        cycle_count += CYCLE
        time.sleep(CYCLE)

def status_controller(working_event, rest_event, battery_safe, break_start, break_end, work_end):
    break_start_hour_min = (break_start.tm_hour, break_start.tm_min)
    break_end_hour_min = (break_end.tm_hour, break_end.tm_min)
    work_end_hour_min = (work_end.tm_hour, work_end.tm_min)
    last_battery_check = time.time()
    before_battery_mode = False
    battery_check_interval = 30

    while working_event.is_set():
        current_time = time.localtime()
        current_hour_min = (current_time.tm_hour, current_time.tm_min)

        if work_end_hour_min and work_end_hour_min <= current_hour_min:
            working_event.clear()
            return
        
        if not rest_event.is_set():
            if break_start_hour_min <= current_hour_min < break_end_hour_min:
                rest_event.set()
            elif battery_safe and (time.time() - last_battery_check > battery_check_interval) and is_battery_mode():
                before_battery_mode = True
                last_battery_check = time.time()
                rest_event.set()
        else:
            if battery_safe and not is_battery_mode() and before_battery_mode:
                rest_event.clear()

        time.sleep(CYCLE)

def is_battery_mode():
    if platform.system() == 'Darwin':
        power_mode = subprocess.run(['pmset', '-g', 'batt'], stdout=subprocess.PIPE, text=True).stdout
        if  'Battery Power' in power_mode:
            return True
    return False

def take_a_rest(rest_event, rest_time):
    rest_event.set()
    try:
        time.sleep(int(rest_time))
    finally:
        rest_event.clear()

def load_config(file_path):
    config = configparser.ConfigParser()
    try:
        config.read(file_path)
        animation = config.get('mode', 'animation', fallback='spinner')
        battery_safe = config.getboolean('mode', 'battery_safe', fallback=True)
        interval = config.getint('time', 'interval', fallback=10)
        break_start = time.strptime(config.get('time', 'break_start', fallback="12:00"), "%H:%M")
        break_end = time.strptime(config.get('time', 'break_end', fallback="13:00"), "%H:%M")
        work_end = time.strptime(config.get('time', 'work_end', fallback="18:00"), "%H:%M")
        return animation, battery_safe, interval, break_start, break_end, work_end
    except (configparser.Error, ValueError) as e:
        print(f"Error loading configuration: {e}. Using default values.")
        return 'spinner', True, 10, time.strptime("12:00", "%H:%M"), time.strptime("13:00", "%H:%M"), time.strptime("18:00", "%H:%M")

def stop_working(working_event, rest_event):
    while working_event.set:
        user_input = input("Press Enter to stop the program...\n")
        if not user_input:
            working_event.clear()
        elif user_input[0] == 'r':
            rest_thread = threading.Thread(target=take_a_rest, args=(rest_event,user_input[1:]))
            rest_thread.daemon = True
            rest_thread.start()

if __name__ == "__main__":
    animation, battery_safe, interval, break_start, break_end, work_end = load_config("config.ini")

    is_working = threading.Event()
    is_resting = threading.Event()
    is_working.set()

    activation_thread = threading.Thread(target=stop_working, args=(is_working,is_resting,))
    timer_thread = threading.Thread(target=status_controller, args=(is_working, is_resting, battery_safe, break_start, break_end, work_end,))
    animation_thread = threading.Thread(target=loading_animation, args=(is_working, is_resting, animation,))
    mouse_thread = threading.Thread(target=move_mouse, args=(is_working, is_resting, interval,))
    
    activation_thread.daemon = True

    activation_thread.start()
    timer_thread.start()
    animation_thread.start()
    mouse_thread.start()

    timer_thread.join()
    animation_thread.join()
    mouse_thread.join()
    
    print("Jobs done...")
