import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from eink_dashboard.config import AppConfig


def get_font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    return int(draw.textlength(text, font=font))


def line_height(font: ImageFont.ImageFont) -> int:
    bbox = font.getbbox("Ag")
    return (bbox[3] - bbox[1]) + 2


def fit_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    if text_width(draw, text, font) <= max_width:
        return text

    shortened = text
    while shortened and text_width(draw, shortened + "...", font) > max_width:
        shortened = shortened[:-1]
    return (shortened + "...") if shortened else ""


def wrap_2_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width_1: int,
    max_width_2: int,
) -> tuple[str, str]:
    words = text.split()
    if not words:
        return "", ""

    line_1 = ""
    index = 0
    while index < len(words):
        candidate = (line_1 + " " + words[index]).strip()
        if text_width(draw, candidate, font) <= max_width_1:
            line_1 = candidate
            index += 1
        else:
            break

    remaining_words = words[index:]
    if not remaining_words:
        return line_1, ""

    line_2 = ""
    index = 0
    while index < len(remaining_words):
        candidate = (line_2 + " " + remaining_words[index]).strip()
        if text_width(draw, candidate, font) <= max_width_2:
            line_2 = candidate
            index += 1
        else:
            break

    if index < len(remaining_words):
        overflow = " ".join(remaining_words[index:])
        line_2 = fit_text(draw, (line_2 + " " + overflow).strip(), font, max_width_2)

    return line_1, line_2


def build_weather_text(config: AppConfig, weather: dict[str, object] | None) -> str:
    city = config.location.city
    if weather and weather.get("temp") is not None:
        return f"{city}: {weather['temp']:.1f}°C {int(weather['hum'])}% {weather['desc']}"
    return f"{city}: no data"


def render_dashboard(epd, config: AppConfig, weather, stock, now: datetime | None = None):
    width, height = epd.height, epd.width
    image = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(image)

    font_small = get_font(12)
    font_medium = get_font(14)
    font_big = get_font(18)

    padding = config.layout.padding
    split_y = config.layout.split_y
    draw.line((0, split_y, width, split_y), fill=0)

    current_time = now or datetime.now()
    time_text = current_time.strftime("%H:%M")
    time_width = text_width(draw, time_text, font_big)
    weather_text = build_weather_text(config, weather)

    y = padding
    font_line_height = line_height(font_medium)
    max_weather_width = width - (2 * padding) - time_width - 6

    if text_width(draw, weather_text, font_medium) <= max_weather_width:
        draw.text((padding, y), weather_text, font=font_medium, fill=0)
        draw.text((width - padding - time_width, y - 1), time_text, font=font_big, fill=0)
        after_header_y = y + font_line_height
    else:
        first_line, second_line = wrap_2_lines(
            draw,
            weather_text,
            font_medium,
            width - (2 * padding),
            max_weather_width,
        )
        draw.text((padding, y), first_line, font=font_medium, fill=0)
        if second_line:
            draw.text((padding, y + font_line_height), second_line, font=font_medium, fill=0)
        draw.text(
            (width - padding - time_width, y + font_line_height - 2),
            time_text,
            font=font_big,
            fill=0,
        )
        after_header_y = y + (2 * font_line_height)

    if weather and weather.get("local"):
        local = weather["local"]
        local_text = (
            f"Bedroom: {local['temperature_c']:.1f}°C {local['humidity_pct']:.0f}% "
            f"Bat {local['battery_pct']}%"
        )
        draw.text((padding, after_header_y + 1), local_text, font=font_small, fill=0)

    stock_y = split_y + 6
    if stock:
        stock_text = f"BMC: {stock['close']:.2f} PLN"
        stock_subtitle = f"{stock.get('date', '')} {stock.get('time', '')}".strip()
    else:
        stock_text = "BMC: no data"
        stock_subtitle = ""

    draw.text((padding, stock_y - 1), stock_text, font=font_big, fill=0)
    if stock_subtitle:
        draw.text((padding, stock_y + 22), stock_subtitle, font=font_small, fill=0)

    return image


def render_centered_text(epd, text: str):
    width, height = epd.height, epd.width
    image = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width_px = bbox[2] - bbox[0]
    text_height_px = bbox[3] - bbox[1]
    x = max(0, (width - text_width_px) // 2)
    y = max(0, (height - text_height_px) // 2)

    draw.text((x, y), text, font=font, fill=0)
    return image.rotate(90, expand=True)

