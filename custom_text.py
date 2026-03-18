#!/usr/bin/env python3
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

import time
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4

def main():
    text = " ".join(sys.argv[1:]).strip() or "Hello from Pi Zero"
    epd = epd2in13_V4.EPD()

    epd.init()
    epd.Clear(0xFF)

    # 2.13" V4 zwykle jest "wąski/wysoki" -> w przykładach rysuje się na (height, width) i obraca
    W, H = epd.height, epd.width
    image = Image.new("1", (W, H), 255)
    draw = ImageDraw.Draw(image)

    # font (pewny na RPi OS)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

    # wyśrodkuj tekst
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = max(0, (W - tw) // 2)
    y = max(0, (H - th) // 2)

    draw.text((x, y), text, font=font, fill=0)

    # obróć do orientacji wyświetlacza
    image = image.rotate(90, expand=True)

    epd.display(epd.getbuffer(image))
    time.sleep(2)
    epd.sleep()

if __name__ == "__main__":
    main()
