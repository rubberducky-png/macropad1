"""
Companion script for the SplashPad macropad's OLED.

Reads your system volume and whatever Windows says is "now playing"
(works with Spotify desktop, browser tabs, or anything else using the
Windows media session -- it's not Spotify-specific, it's whatever has
focus of the system media controls) and streams both to the XIAO
RP2040 over its USB data serial port, about once a second.

Setup:
    pip install pyserial pycaw comtypes winsdk

Usage:
    python pc_bridge.py            # auto-detects the board's COM port
    python pc_bridge.py COM7       # or force a specific port

Requires boot.py (enabling usb_cdc data) to already be on the board,
and the board to have been reset/replugged after copying it over.
"""

import asyncio
import json
import sys

import serial
import serial.tools.list_ports

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
)

POLL_SECONDS = 1.5


def find_port():
    if len(sys.argv) > 1:
        return sys.argv[1]
    for p in serial.tools.list_ports.comports():
        desc = p.description or ""
        if "CircuitPython" in desc or "XIAO" in desc:
            return p.device
    raise RuntimeError(
        "Couldn't auto-find the board's serial port. Check Device Manager "
        "for its COM port and run: python pc_bridge.py COMx"
    )


def get_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return round(volume.GetMasterVolumeLevelScalar() * 100)


async def get_media_info():
    manager = await MediaManager.request_async()
    session = manager.get_current_session()
    if session is None:
        return None, None, False

    info = await session.try_get_media_properties_async()
    playback_info = session.get_playback_info()
    is_playing = playback_info.playback_status == PlaybackStatus.PLAYING
    return info.title, info.artist, is_playing


async def main():
    port_name = find_port()
    print("Connecting to {}...".format(port_name))
    ser = serial.Serial(port_name, baudrate=115200, timeout=1)

    while True:
        try:
            vol = get_volume()
        except Exception as e:
            print("Volume read failed:", e)
            vol = None

        try:
            title, artist, playing = await get_media_info()
        except Exception as e:
            print("Media read failed:", e)
            title, artist, playing = None, None, False

        payload = {
            "vol": vol,
            "song": title,
            "artist": artist,
            "playing": playing,
        }

        try:
            ser.write((json.dumps(payload) + "\n").encode("utf-8"))
        except Exception as e:
            print("Serial write failed:", e)

        await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
