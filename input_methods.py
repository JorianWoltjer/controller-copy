from abc import ABC, abstractmethod
from dataclasses import dataclass
from pyxinput import vController, rController
from time import sleep
import keyboard
import win32api  # Detecting mouse presses
import hid

@dataclass
class Stick:
    x: int = 0  # 32768-32767
    y: int = 0  # 32768-32767
    pressed: bool = False

@dataclass
class Report:
    stick_l: Stick = Stick()
    stick_r: Stick = Stick()
    button_a: bool = False
    button_b: bool = False
    button_x: bool = False
    button_y: bool = False
    button_back: bool = False
    button_start: bool = False
    button_shoulder_l: bool = False
    button_shoulder_r: bool = False
    dpad: int = 0  # Combination of Dpad enum
    trigger_l: int = 0  # 0-255
    trigger_r: int = 0  # 0-255

class InputMethod(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def get_report(self) -> Report:
        pass

class KeyboardInput(InputMethod):
    def get_report(self) -> Report:
        report = Report()
        
        # Sticks
        stick_lx = stick_ly = stick_rx = stick_ry = 0
        if keyboard.is_pressed('d'): stick_lx += 32767
        if keyboard.is_pressed('a'): stick_lx -= 32768
        if keyboard.is_pressed('w'): stick_ly += 32767
        if keyboard.is_pressed('s'): stick_ly -= 32768
        if keyboard.is_pressed('right'): stick_rx += 32767
        if keyboard.is_pressed('left'): stick_rx -= 32768
        if keyboard.is_pressed('up'): stick_ry += 32767
        if keyboard.is_pressed('down'): stick_ry -= 32768
        report.stick_l.x = stick_lx
        report.stick_l.y = stick_ly
        report.stick_r.x = stick_rx
        report.stick_r.y = stick_ry
        
        # Buttons
        report.button_a = keyboard.is_pressed('space') or keyboard.is_pressed('enter')
        report.button_b = keyboard.is_pressed('q') or win32api.GetKeyState(0x02) < 0  # 0x02 = Right click
        report.button_x = keyboard.is_pressed('e')
        report.button_y = win32api.GetKeyState(0x05) < 0  # 0x05 = Back mouse side button
        
        # Special buttons
        report.stick_l.pressed = keyboard.is_pressed('ctrl')
        report.stick_r.pressed = win32api.GetKeyState(0x06) < 0  # 0x06 = Forward mouse side button
        report.button_start = keyboard.is_pressed('esc')
        report.button_back = keyboard.is_pressed('tab')
        report.button_shoulder_l = keyboard.is_pressed('shift')
        report.button_shoulder_r = win32api.GetKeyState(0x01) < 0  # 0x01 = Left click

        # Dpad
        dpad = 0
        if keyboard.is_pressed('up')    or keyboard.is_pressed('1'): dpad += vController.DPAD_UP
        if keyboard.is_pressed('down')  or keyboard.is_pressed('4'): dpad += vController.DPAD_DOWN
        if keyboard.is_pressed('left')  or keyboard.is_pressed('2'): dpad += vController.DPAD_LEFT
        if keyboard.is_pressed('right') or keyboard.is_pressed('3'): dpad += vController.DPAD_RIGHT
        report.dpad = dpad
        
        # Triggers
        report.trigger_l = 255 if keyboard.is_pressed('s') else 0
        report.trigger_r = 255 if keyboard.is_pressed('w') else 0
        
        return report


class PS4ControllerInput(InputMethod):
    def __init__(self):
        self.gamepad = hid.device()
        # Find controller to read from
        for device in hid.enumerate():
            if 'Controller' in device['product_string']:
                print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")
                self.gamepad.open(device['vendor_id'], device['product_id'])
                self.gamepad.set_nonblocking(True)
                break
        else:
            print("PS4 Controller not found")
            exit()
    
    def convert_stick(value, invert=False):
        """Convert 0-255 value into 32768-32767 value"""
        # Super bad code, just don't touch it, it works :)
        if not invert:
            result = value * 256 - 32768
            if result > 0:
                result += 255
        else:
            result = ((256-value)*256 - 32768) - 1
            if result < -1:
                result -= 255
            elif result == -1:
                result = 0
        
        return result
    
    def convert_dpad(value):
        if value == 7:
            return vController.DPAD_UP | vController.DPAD_LEFT
        elif value == 6:
            return vController.DPAD_LEFT
        elif value == 5:
            return vController.DPAD_DOWN | vController.DPAD_LEFT
        elif value == 4:
            return vController.DPAD_DOWN
        elif value == 3:
            return vController.DPAD_DOWN | vController.DPAD_RIGHT
        elif value == 2:
            return vController.DPAD_RIGHT
        elif value == 1:
            return vController.DPAD_UP | vController.DPAD_RIGHT
        elif value == 0:
            return vController.DPAD_UP
        else:
            return vController.DPAD_OFF
    
    def reading_to_int(reading):
        """Convert array of bytes into a big integer, to read bits from"""
        n = 0
        for value in reading[:10]:
            n <<= 8
            n += value
        
        return n
    
    def get_report(self) -> Report:
        report = Report()
        
        reading = []
        while not reading:
            reading = self.gamepad.read(64)

        r = PS4ControllerInput.reading_to_int(reading)
        
        report.stick_l.x = PS4ControllerInput.convert_stick(r>>64 & 0xff)
        report.stick_l.y = PS4ControllerInput.convert_stick(r>>56 & 0xff, invert=True)
        report.stick_r.x = PS4ControllerInput.convert_stick(r>>48 & 0xff)
        report.stick_r.y = PS4ControllerInput.convert_stick(r>>40 & 0xff, invert=True)
        # Buttons
        report.button_y = bool(r>>39 & 1)
        report.button_b = bool(r>>38 & 1)
        report.button_a = bool(r>>37 & 1)
        report.button_x = bool(r>>36 & 1)
        # Dpad
        report.dpad = PS4ControllerInput.convert_dpad(r>>32 & 0xf)
        # Special buttons
        report.stick_r.pressed = bool(r>>31 & 1)
        report.stick_l.pressed = bool(r>>30 & 1)
        report.button_start =    bool(r>>29 & 1)
        report.button_back  =    bool(r>>28 & 1)
        #n>>27 & 1 = TriggerR pressed (not used)
        #n>>26 & 1 = TriggerL pressed (not used)
        report.button_shoulder_r = bool(r>>25 & 1)
        report.button_shoulder_l = bool(r>>24 & 1)
        #n>>18 & 6 = TriggerR pressed (not used)
        #n>>17 & 1 = Tpad click (not used)
        #n>>16 & 1 = Playstation logo (not used)
        # Triggers
        report.trigger_l = r>>8 & 0xff
        report.trigger_r = r>>0 & 0xff
        
        return report
    
class XboxControllerInput(InputMethod):
    def __init__(self):
        self.controller = rController(1)
    
    def get_report(self) -> Report:
        report = Report()
        
        gamepad = self.controller.gamepad
        pressed_buttons = self.controller.buttons
        
        # Stick
        report.stick_l.x = gamepad['thumb_lx']
        report.stick_l.y = gamepad['thumb_ly']
        report.stick_r.x = gamepad['thumb_rx']
        report.stick_r.y = gamepad['thumb_ry']
        
        # Buttons
        report.button_a = 'A' in pressed_buttons
        report.button_b = 'B' in pressed_buttons
        report.button_x = 'X' in pressed_buttons
        report.button_y = 'Y' in pressed_buttons
        
        # Special buttons
        report.stick_l.pressed = 'LEFT_THUMB' in pressed_buttons
        report.stick_r.pressed = 'RIGHT_THUMB' in pressed_buttons
        report.button_start = 'START' in pressed_buttons
        report.button_back = 'BACK' in pressed_buttons
        report.button_shoulder_l = 'LEFT_SHOULDER' in pressed_buttons
        report.button_shoulder_r = 'RIGHT_SHOULDER' in pressed_buttons
        
        # Dpad
        dpad = 0
        if 'DPAD_UP' in pressed_buttons:
            dpad += vController.DPAD_UP
        if 'DPAD_DOWN' in pressed_buttons:
            dpad += vController.DPAD_DOWN
        if 'DPAD_LEFT' in pressed_buttons:
            dpad += vController.DPAD_LEFT
        if 'DPAD_RIGHT' in pressed_buttons:
            dpad += vController.DPAD_RIGHT
        report.dpad = dpad

        # Triggers
        report.trigger_l = gamepad['left_trigger']
        report.trigger_r = gamepad['right_trigger']
        
        return report

if __name__ == "__main__":
    input = XboxControllerInput()

    while True:
        report = input.get_report()
        
        print(report)
        sleep(0.2)
