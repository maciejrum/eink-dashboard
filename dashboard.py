#!/usr/bin/env python3
import os
os.environ.setdefault("GPIOZERO_PIN_FACTORY", "lgpio")  # przed importem waveshare

import json
import csv
import ssl
import urllib.request
from datetime import datetime
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
import asyncio

# waveshare lib z repo (bez instalacji paczki)
import sys as _sys
_sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
from waveshare_epd import epd2in13_V4
from bleak import BleakScanner


CITY = "Kraków"
LAT, LON = 50.0647, 19.9450
TZ = "Europe/Warsaw"

STOOQ_SYMBOLS = ["bmc", "bmc.pl"]
STOOQ_QUOTE_URL = "https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv"

BT_HOME_UUID = "0000fcd2-0000-1000-8000-00805f9b34fb"
# Na Linuxie adres to zwykle MAC; na macOS widac UUID.
BT_TARGET_ADDR = ""
BT_TARGET_NAME = "ATC_032E2A"

PADDING = 4
SPLIT_Y = 62  # linia podziału (góra/dół)

WMO_DESC_PL = {
    0: "bezchm.", 1: "prawie", 2: "częściowe", 3: "pochm.",
    45: "mgła", 48: "mgła",
    51: "mżawka", 53: "mżawka", 55: "mżawka",
    61: "deszcz", 63: "deszcz", 65: "deszcz",
    71: "śnieg", 73: "śnieg", 75: "śnieg",
    80: "przelotny", 81: "przelotny", 82: "ulewa",
    95: "burza", 96: "burza", 99: "burza",
}


def fetch_bytes(url: str, timeout: int = 6) -> bytes:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "pi-zero-eink/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read()


def get_font(size: int) -> ImageFont.ImageFont:
    # pewne fonty na RPi OS (a jak nie ma, to fallback)
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def text_w(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    return int(draw.textlength(text, font=font))


def line_h(font: ImageFont.ImageFont) -> int:
    b = font.getbbox("Ag")
    return (b[3] - b[1]) + 2


def fit_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_w: int) -> str:
    if text_w(draw, text, font) <= max_w:
        return text
    s = text
    while s and text_w(draw, s + "…", font) > max_w:
        s = s[:-1]
    return (s + "…") if s else ""


def wrap_2_lines(draw, text, font, max_w1, max_w2):
    # word-wrap do max 2 linii, druga z innym max_w
    words = text.split()
    if not words:
        return "", ""

    line1 = ""
    i = 0
    while i < len(words):
        cand = (line1 + " " + words[i]).strip()
        if text_w(draw, cand, font) <= max_w1:
            line1 = cand
            i += 1
        else:
            break

    rest = words[i:]
    if not rest:
        return line1, ""

    line2 = ""
    j = 0
    while j < len(rest):
        cand = (line2 + " " + rest[j]).strip()
        if text_w(draw, cand, font) <= max_w2:
            line2 = cand
            j += 1
        else:
            break

    if j < len(rest):
        line2 = fit_text(draw, line2 + " " + " ".join(rest[j:]), font, max_w2)

    return line1, line2


def get_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&current=temperature_2m,relative_humidity_2m,weather_code"
        f"&timezone={TZ}"
    )
    data = json.loads(fetch_bytes(url).decode("utf-8"))
    cur = data.get("current", {})
    temp = cur.get("temperature_2m")
    hum = cur.get("relative_humidity_2m")
    code = cur.get("weather_code")
    desc = WMO_DESC_PL.get(code, f"kod {code}")
    return {"temp": temp, "hum": hum, "desc": desc}


def parse_stooq_quote(csv_text: str):
    rows = list(csv.DictReader(csv_text.splitlines()))
    if not rows:
        return None
    r = rows[0]
    try:
        close = float(r["Close"])
    except Exception:
        return None
    return {
        "symbol": r.get("Symbol"),
        "date": r.get("Date"),
        "time": r.get("Time"),
        "close": close,
        "currency": "PLN",
    }


def get_stock_cdr():
    last_err = None
    for sym in STOOQ_SYMBOLS:
        try:
            url = STOOQ_QUOTE_URL.format(sym=sym)
            txt = fetch_bytes(url).decode("utf-8", errors="replace")
            q = parse_stooq_quote(txt)
            if q:
                return q
        except Exception as e:
            last_err = e
    raise RuntimeError(f"stooq fail: {last_err}")


def decode_fixed_bthome(data: bytes):
    if len(data) != 11:
        return None
    if data[0] != 0x40 or data[1] != 0x00:
        return None
    if not (data[3] == 0x01 and data[5] == 0x02 and data[8] == 0x03):
        return None

    pid = data[2]
    batt = data[4]
    temp_raw = int.from_bytes(data[6:8], "little", signed=True)
    hum_raw = int.from_bytes(data[9:11], "little", signed=False)

    return {
        "pid": pid,
        "battery_pct": batt,
        "temperature_c": temp_raw / 100.0,
        "humidity_pct": hum_raw / 100.0,
    }


async def read_ble_once(timeout_s: float = 8.0):
    got = asyncio.Event()
    result = {}

    def cb(dev, adv):
        if BT_TARGET_ADDR and dev.address != BT_TARGET_ADDR:
            return
        if BT_TARGET_NAME and dev.name != BT_TARGET_NAME:
            return
        data = (adv.service_data or {}).get(BT_HOME_UUID)
        if not data:
            return
        d = decode_fixed_bthome(data)
        if not d:
            return
        result.update(d)
        got.set()

    scanner = BleakScanner(cb)
    await scanner.start()
    try:
        await asyncio.wait_for(got.wait(), timeout=timeout_s)
    finally:
        await scanner.stop()

    return result


def get_ble_sensor():
    try:
        return asyncio.run(read_ble_once())
    except Exception:
        return None


def render_image(epd, weather, stock):
    W, H = epd.height, epd.width  # 250 x 122 dla 2.13 V4
    img = Image.new("1", (W, H), 255)
    draw = ImageDraw.Draw(img)

    font_s = get_font(12)
    font_m = get_font(14)
    font_b = get_font(18)

    # linia podziału
    draw.line((0, SPLIT_Y, W, SPLIT_Y), fill=0)

    # --- HEADER ---
    now = datetime.now()
    time_str = now.strftime("%H:%M")
    time_w = text_w(draw, time_str, font_b)

    if weather and weather.get("temp") is not None:
        wtxt = f"{CITY}: {weather['temp']:.1f}°C {int(weather['hum'])}% {weather['desc']}"
    else:
        wtxt = f"{CITY}: brak danych"

    y1 = PADDING
    lh = line_h(font_m)

    # próba: zmieścić pogodę + godzinę w 1 linii
    max_weather_1line = W - 2 * PADDING - time_w - 6
    if text_w(draw, wtxt, font_m) <= max_weather_1line:
        draw.text((PADDING, y1), wtxt, font=font_m, fill=0)
        draw.text((W - PADDING - time_w, y1 - 1), time_str, font=font_b, fill=0)
        y_after_header = y1 + lh
    else:
        # pogoda w 2 linie, godzina w 2 linii po prawej
        max_w1 = W - 2 * PADDING
        max_w2 = W - 2 * PADDING - time_w - 6

        l1, l2 = wrap_2_lines(draw, wtxt, font_m, max_w1, max_w2)
        draw.text((PADDING, y1), l1, font=font_m, fill=0)
        if l2:
            draw.text((PADDING, y1 + lh), l2, font=font_m, fill=0)

        # godzina na drugiej linii, prawa strona
        draw.text((W - PADDING - time_w, y1 + lh - 2), time_str, font=font_b, fill=0)
        y_after_header = y1 + (2 * lh)

    # --- LOCAL BLE SENSOR ---
    if weather and weather.get("local"):
        d = weather["local"]
        local_txt = (
            f"Syp: Temp: {d['temperature_c']:.1f}°C Hum: {d['humidity_pct']:.0f}% "
            f"Bat{d['battery_pct']}%"
        )
        draw.text((PADDING, y_after_header + 1), local_txt, font=font_s, fill=0)

    # --- BOTTOM: BMC ---
    x = PADDING
    y = SPLIT_Y + 6

    if stock:
        stxt = f"BMC: {stock['close']:.2f} PLN"
        sub = f"{stock.get('date','')} {stock.get('time','')}".strip()
    else:
        stxt = "BMC: brak danych"
        sub = ""

    draw.text((x, y - 1), stxt, font=font_b, fill=0)
    if sub:
        draw.text((x, y + 22), sub, font=font_s, fill=0)

    return img


def seconds_until_next_half_hour(now: datetime) -> float:
    # Najblizszy slot: pelna godzina lub +30 min
    minute = now.minute
    if minute < 30:
        target_minute = 30
        target_hour = now.hour
        target_date = now.date()
    else:
        target_minute = 0
        target_hour = (now.hour + 1) % 24
        target_date = now.date()
        if target_hour == 0:
            target_date = now.date().fromordinal(now.date().toordinal() + 1)

    target = datetime(
        year=target_date.year,
        month=target_date.month,
        day=target_date.day,
        hour=target_hour,
        minute=target_minute,
        second=0,
    )
    return max(0.0, (target - now).total_seconds())


def main():
    epd = epd2in13_V4.EPD()
    epd.init()

    try:
        while True:
            time.sleep(seconds_until_next_half_hour(datetime.now()))

            try:
                weather = get_weather()
            except Exception:
                weather = None

            try:
                stock = get_stock_cdr()
            except Exception:
                stock = None

            local = None
            while local is None:
                local = get_ble_sensor()
                if local is None:
                    time.sleep(10)

            if weather is None:
                weather = {}
            weather["local"] = local

            img = render_image(epd, weather, stock)
            img = img.rotate(180)
            epd.display(epd.getbuffer(img))
    except KeyboardInterrupt:
        pass
    finally:
        epd.sleep()


if __name__ == "__main__":
    main()
