from datetime import datetime
import unittest

from eink_dashboard.config import DEFAULT_CONFIG
from eink_dashboard.rendering import build_weather_text, render_dashboard, wrap_2_lines

from PIL import Image, ImageDraw, ImageFont


class FakeEPD:
    height = 250
    width = 122


class RenderingTests(unittest.TestCase):
    def test_build_weather_text_handles_missing_data(self):
        self.assertEqual(build_weather_text(DEFAULT_CONFIG, None), "Kraków: no data")

    def test_wrap_2_lines_returns_two_lines(self):
        image = Image.new("1", (250, 122), 255)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        line_1, line_2 = wrap_2_lines(
            draw,
            "This is a long line that should wrap",
            font,
            60,
            60,
        )

        self.assertTrue(line_1)
        self.assertTrue(line_2)

    def test_render_dashboard_returns_expected_canvas_size(self):
        weather = {"temp": 21.3, "hum": 48, "desc": "clear", "local": {"temperature_c": 22.1, "humidity_pct": 40, "battery_pct": 90}}
        stock = {"close": 123.45, "date": "2026-03-18", "time": "12:00"}

        image = render_dashboard(FakeEPD(), DEFAULT_CONFIG, weather, stock, now=datetime(2026, 3, 18, 14, 30))

        self.assertEqual(image.size, (250, 122))

