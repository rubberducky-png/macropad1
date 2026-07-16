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

# --- Key Matrix (3x3) ---
# Pins traced from macropad.kicad_pcb (XIAO RP2040 pad -> net):
#   Row 0 = D0 (top)     Row 1 = D1 (middle)   Row 2 = D6 (bottom)
#   Col 0 = D10 (left)   Col 1 = D9 (middle)   Col 2 = D8 (right)
# Diodes go switch -> row (cathode on the Row net), so this is COL2ROW.
keyboard.col_pins = (board.D10, board.D9, board.D8)
keyboard.row_pins = (board.D0, board.D1, board.D6)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# --- Rotary Encoder (top area, A/B only) ---
# PCB net trace: encoder A -> D2, encoder B -> D3.
# The encoder footprint DOES have push-button pins (MP/S2), but they land
# on nets RNSWA/RNSWB which aren't routed to any XIAO pin -- confirms the
# click function isn't wired on this board, so no button_pin here.
encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)
encoder_handler.pins = (
    (board.D2, board.D3, None),
)

# --- RGB LEDs ---
# LED Data -> D7. The board has 12 SK6812 LEDs on this data line (9 under
# the keys in a 3x3 grid + 3 more in a 4th column off to the side, near
# the encoder) -- adjust num_pixels if that's not what you intended.
rgb = RGB(
    pixel_pin=board.D7,
    num_pixels=12,
    animation_mode=AnimationModes.STATIC,
    hue_default=160,     # blue
    val_default=100,
)
keyboard.extensions.append(rgb)

# --- OLED (128x32 SSD1306, I2C: SDA -> D4, SCL -> D5) ---
displayio.release_displays()
i2c = busio.I2C(scl=board.D5, sda=board.D4)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

splash = displayio.Group()
display.root_group = splash

# Three lines: volume/RGB mode are ~8px tall each, song title on the
# bottom row. main.py updates these labels' .text as data comes in.
vol_label = label.Label(terminalio.FONT, text="Vol: --", x=0, y=4)
rgb_label = label.Label(terminalio.FONT, text="RGB: --", x=0, y=14)
song_label = label.Label(terminalio.FONT, text="Song: --", x=0, y=25)
splash.append(vol_label)
splash.append(rgb_label)
splash.append(song_label)

# NOTE: i2cdisplaybus is the CircuitPython 9.x module name. If you're on
# CircuitPython 8.x, replace the two lines above with:
#   display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
