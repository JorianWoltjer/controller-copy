from threading import Thread
from pynput.keyboard import Listener
from pyxinput import vController
from time import sleep

from input_methods import Report, KeyboardInput, PS4ControllerInput, XboxControllerInput


# Select one of the INPUTs:
INPUT = KeyboardInput()
# INPUT = PS4ControllerInput()
# INPUT = XboxControllerInput()
EXTRA_CONTROLLERS = 3  # Number of controllers to create

controllers = []  # (controller, enabled)

def press_buttons(controller: vController, report: Report):
    controller.set_value('AxisLx', report.stick_l.x)
    controller.set_value('AxisLy', report.stick_l.y)
    controller.set_value('AxisRx', report.stick_r.x)
    controller.set_value('AxisRy', report.stick_r.y)
    controller.set_value('BtnA', report.button_a)
    controller.set_value('BtnB', report.button_b)
    controller.set_value('BtnX', report.button_x)
    controller.set_value('BtnY', report.button_y)
    controller.set_value('Dpad', report.dpad)
    controller.set_value('BtnThumbL', report.stick_l.pressed)
    controller.set_value('BtnThumbR', report.stick_r.pressed)
    controller.set_value('BtnStart', report.button_start)
    controller.set_value('BtnBack', report.button_back)
    controller.set_value('BtnShoulderR', report.button_shoulder_r)
    controller.set_value('BtnShoulderL', report.button_shoulder_l)
    controller.set_value('TriggerL', report.trigger_l)
    controller.set_value('TriggerR', report.trigger_r)
    
def join_rocket_league(controller: vController):
    controller.set_value('BtnA', 1)
    sleep(0.2)
    controller.set_value('BtnA', 0)


def on_keyboard_press(key):
    if hasattr(key, 'vk') and 96 <= key.vk <= 105:  # If numpad
        number = key.vk - 97
        if number == -1:  # 0 pressed, enable all
            selected = [0, 1, 2, 3]
        elif number < len(controllers):  # Enable specific index
            selected = [number]
        else:
            return
            
        print("Selected", selected)
        for i in range(len(controllers)):  # Set enabled
            controllers[i] = (controllers[i][0], i in selected)

def listen():
    with Listener(on_press=on_keyboard_press) as listener:
        listener.join()

# Keyboard controls (1234 toggle)
t = Thread(target=listen)
t.daemon = True
t.start()

# Create virtual controllers
if not isinstance(INPUT, XboxControllerInput):
    # Add one dummy controller to push other controllers one further (2, 3, 4...)
    dummy = (vController(percent=False), True)
    if not isinstance(INPUT, KeyboardInput):
        controllers.append(dummy)

controllers += [(vController(percent=False), True) for _ in range(EXTRA_CONTROLLERS)]

# Join Rocket League (optional)
for controller, enabled in controllers:
    if enabled:
        controller.set_value('BtnStart', 1)

sleep(3)  # Time to Alt+Tab into game

for controller, enabled in controllers:
    if enabled:
        print(f"Player {controller.id} joined")
        join_rocket_league(controller)
        controller.set_value('BtnStart', 0)
        sleep(0.5)

# Copy loop
while True:
    report = INPUT.get_report()
    # print(report)
    
    for controller, enabled in controllers:
        if enabled:
            press_buttons(controller, report)
