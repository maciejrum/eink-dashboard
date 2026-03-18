import time

from eink_dashboard.display import create_epd
from eink_dashboard.rendering import render_centered_text


def show_text(text: str):
    epd = create_epd()
    epd.init()
    epd.Clear(0xFF)
    epd.display(epd.getbuffer(render_centered_text(epd, text)))
    time.sleep(2)
    epd.sleep()

