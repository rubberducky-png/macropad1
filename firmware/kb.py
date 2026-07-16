import board
import busio
import displayio
import i2cdisplaybus
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

from kmk.kmk_keyboard import KMKKeyboard
from kmk.matrix import DiodeOrientation
from kmk.modules.encoder import EncoderHandler
from kmk.extensions.RGB import RGB, AnimationModes

keyboard = KMKKeyboard()

keyboard.col_pins = (board.D10, board.D9, board.D8)
keyboard.row_pins = (board.D0, board.D1, board.D6)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)
encoder_handler.pins = (
    (board.D2, board.D3, None),
)


rgb = RGB(
    pixel_pin=board.D7,
    num_pixels=12,
    animation_mode=AnimationModes.STATIC,
    hue_default=160,     
    val_default=100,
)
keyboard.extensions.append(rgb)

displayio.release_displays()
i2c = busio.I2C(scl=board.D5, sda=board.D4)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

splash = displayio.Group()
display.root_group = splash

vol_label = label.Label(terminalio.FONT, text="Vol: --", x=0, y=4)
rgb_label = label.Label(terminalio.FONT, text="RGB: --", x=0, y=14)
song_label = label.Label(terminalio.FONT, text="Song: --", x=0, y=25)
splash.append(vol_label)
splash.append(rgb_label)
splash.append(song_label)
