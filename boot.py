import usb_cdc

# console=True keeps the normal CircuitPython REPL/serial console alive.
# data=True opens a second, separate serial channel that pc_bridge.py
# uses to send volume / now-playing info to the board.
#
# boot.py only runs on hardware boot/reset -- after copying this to the
# board, unplug it and plug it back in (or hit reset) for it to take
# effect.
usb_cdc.enable(console=True, data=True)
