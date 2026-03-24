from dataclasses import replace
import unittest
from unittest.mock import patch

from eink_dashboard.app import build_payload, safe_get_local_sensor
from eink_dashboard.config import DEFAULT_CONFIG


class AppTests(unittest.TestCase):
    def test_build_payload_continues_without_ble_data(self):
        with patch("eink_dashboard.app.safe_get_weather", return_value={"temp": 21.0}):
            with patch("eink_dashboard.app.safe_get_local_sensor", return_value=None):
                with patch("eink_dashboard.app.safe_get_stock_quote", return_value={"close": 123.45}):
                    weather, stock = build_payload(DEFAULT_CONFIG)

        self.assertEqual(weather, {"temp": 21.0, "local": None})
        self.assertEqual(stock, {"close": 123.45})

    def test_safe_get_local_sensor_returns_none_after_single_failed_attempt(self):
        config = replace(DEFAULT_CONFIG, ble=replace(DEFAULT_CONFIG.ble, target_name="", target_addr=""))

        with patch("eink_dashboard.app.get_ble_sensor", return_value=None) as mocked_get_ble_sensor:
            result = safe_get_local_sensor(config)

        self.assertIsNone(result)
        mocked_get_ble_sensor.assert_called_once_with(config)
