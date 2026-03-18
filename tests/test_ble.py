import unittest

from eink_dashboard.providers.ble import decode_fixed_bthome


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

