import json
import usb_cdc

from kb import keyboard, encoder_handler, rgb, vol_label, rgb_label, song_label
from kmk.keys import KC
from kmk.modules import Module
from kmk.modules.macros import Macros
from kmk.extensions.RGB import AnimationModes

macros = Macros()
keyboard.modules.append(macros)

KC_NETFLIX = KC.MACRO(
    KC.LGUI, 150,
    'netflix', 300,
    KC.ENTER,
)

KC_SPOTIFY = KC.MACRO(
    KC.LGUI, 150,
    'spotify', 300,
    KC.ENTER,
)

KC_VSCODE = KC.MACRO(
    KC.LGUI, 150,
    'visual studio code', 400,
    KC.ENTER,
)


LED_MODES = [
    AnimationModes.BREATHING,          
    AnimationModes.RAINBOW,             
    AnimationModes.SWIRL,               
    AnimationModes.BREATHING_RAINBOW,  
    None,                              
]
LED_MODE_NAMES = ["Solid", "Rainbow", "Wave", "Grid Fade", "Off"]
_led_mode_index = 0


def cycle_led_modes(key, keyboard, *args):
    global _led_mode_index
    _led_mode_index = (_led_mode_index + 1) % len(LED_MODES)
    mode = LED_MODES[_led_mode_index]

    if mode is None:
        rgb.enable = False
    else:
        rgb.enable = True
        rgb.animation_mode = mode
        if mode == AnimationModes.BREATHING:
            rgb.hue = 160  

    rgb_label.text = "RGB: " + LED_MODE_NAMES[_led_mode_index]

    return keyboard


KC_LED_CYCLE = KC.new_key(on_press=cycle_led_modes)


SONG_LINE_MAX_CHARS = 21 


class PCBridge(Module):
    def __init__(self):
        self._serial = usb_cdc.data
        self._buf = ""

    def during_bootup(self, keyboard):
        return

    def before_matrix_scan(self, keyboard):
        if self._serial is None or not self._serial.in_waiting:
            return keyboard

        try:
            chunk = self._serial.read(self._serial.in_waiting).decode("utf-8")
        except Exception:
            return keyboard

        self._buf += chunk
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._handle_line(line.strip())

        return keyboard

    def _handle_line(self, line):
        if not line:
            return
        try:
            data = json.loads(line)
        except ValueError:
            return

        vol = data.get("vol")
        if vol is not None:
            vol_label.text = "Vol: {}%".format(vol)

        if data.get("playing") and data.get("song"):
            artist = data.get("artist")
            text = "{} - {}".format(data["song"], artist) if artist else data["song"]
            song_label.text = text[:SONG_LINE_MAX_CHARS]
        else:
            song_label.text = "No media playing"

    def after_matrix_scan(self, keyboard):
        return keyboard

    def process_key(self, keyboard, key_event):
        return key_event

    def before_hid_send(self, keyboard):
        return keyboard

    def after_hid_send(self, keyboard):
        return keyboard

    def on_powersave_enable(self, keyboard):
        return keyboard

    def on_powersave_disable(self, keyboard):
        return keyboard


keyboard.modules.append(PCBridge())

keyboard.keymap = [
    [
        KC.MRWD,     KC.MPLY,     KC.MFFD,
        KC_NETFLIX,  KC_SPOTIFY,  KC_VSCODE,
        KC.LEFT,     KC.RIGHT,    KC_LED_CYCLE,
    ]
]


encoder_handler.map = [
    ((KC.VOLD, KC.VOLU),),
]

if __name__ == '__main__':
    keyboard.go()
