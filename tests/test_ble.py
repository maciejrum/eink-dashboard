from dataclasses import replace
import unittest
from unittest.mock import patch

from eink_dashboard.config import DEFAULT_CONFIG
from eink_dashboard.providers.ble import decode_fixed_bthome, get_ble_sensor
class FakeDevice:
    def __init__(self, address: str, name: str):
        self.address = address
        self.name = name


class FakeAdvertisement:
    def __init__(self, service_data):
        self.service_data = service_data


class FakeBleakScanner:
    def __init__(self, callback):
        self.callback = callback

    async def start(self):
        payload = bytes([0x40, 0x00, 0x2A, 0x01, 95, 0x02, 0x2E, 0x09, 0x03, 0x2C, 0x1A])
        self.callback(
            FakeDevice(address="AA:BB:CC:DD:EE:FF", name="ATC_TEST"),
            FakeAdvertisement(service_data={DEFAULT_CONFIG.ble.service_uuid: payload}),
        )

    async def stop(self):
        return None


class DecodeFixedBTHomeTests(unittest.TestCase):
    def test_decodes_expected_payload(self):
        payload = bytes([0x40, 0x00, 0x2A, 0x01, 95, 0x02, 0x2E, 0x09, 0x03, 0x2C, 0x1A])

        decoded = decode_fixed_bthome(payload)

        self.assertEqual(decoded["pid"], 0x2A)
        self.assertEqual(decoded["battery_pct"], 95)
        self.assertEqual(decoded["temperature_c"], 23.5)
        self.assertEqual(decoded["humidity_pct"], 67.0)

    def test_rejects_invalid_payload_shape(self):
        self.assertIsNone(decode_fixed_bthome(b"short"))
        self.assertIsNone(decode_fixed_bthome(bytes([0] * 11)))


class GetBleSensorTests(unittest.TestCase):
    def test_get_ble_sensor_returns_decoded_data_from_matching_advertisement(self):
        config = replace(DEFAULT_CONFIG, ble=replace(DEFAULT_CONFIG.ble, target_name="ATC_TEST"))

        with patch("eink_dashboard.providers.ble.BleakScanner", FakeBleakScanner):
            decoded = get_ble_sensor(config)

        self.assertEqual(
            decoded,
            {
                "pid": 0x2A,
                "battery_pct": 95,
                "temperature_c": 23.5,
                "humidity_pct": 67.0,
            },
        )

    def test_get_ble_sensor_ignores_non_matching_advertisement(self):
        config = replace(DEFAULT_CONFIG, ble=replace(DEFAULT_CONFIG.ble, target_name="OTHER_SENSOR", timeout_s=0.01))

        with patch("eink_dashboard.providers.ble.BleakScanner", FakeBleakScanner):
            decoded = get_ble_sensor(config)

        self.assertIsNone(decoded)
