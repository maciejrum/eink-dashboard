import os
import sys


os.environ.setdefault("GPIOZERO_PIN_FACTORY", "lgpio")
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib"))

from waveshare_epd import epd2in13_V4  # noqa: E402


def create_epd():
    return epd2in13_V4.EPD()

