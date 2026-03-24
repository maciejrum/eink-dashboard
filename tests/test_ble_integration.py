import os
import unittest
from dataclasses import replace

from eink_dashboard.config import DEFAULT_CONFIG
from eink_dashboard.providers.ble import get_ble_sensor


RUN_BLE_INTEGRATION = os.getenv("RUN_BLE_INTEGRATION") == "1"


@unittest.skipUnless(
    RUN_BLE_INTEGRATION,
    "Set RUN_BLE_INTEGRATION=1 to run against a real BLE sensor",
)
class BleIntegrationTests(unittest.TestCase):
    def test_reads_real_ble_sensor_data(self):
        timeout_s = float(os.getenv("EINK_BT_TIMEOUT_S", "20"))
        target_name = os.getenv("EINK_BT_TARGET_NAME", DEFAULT_CONFIG.ble.target_name)
        target_addr = os.getenv("EINK_BT_TARGET_ADDR", DEFAULT_CONFIG.ble.target_addr)
        service_uuid = os.getenv("EINK_BT_HOME_UUID", DEFAULT_CONFIG.ble.service_uuid)

        config = replace(
            DEFAULT_CONFIG,
            ble=replace(
                DEFAULT_CONFIG.ble,
                target_name=target_name,
                target_addr=target_addr,
                service_uuid=service_uuid,
                timeout_s=timeout_s,
            ),
        )

        decoded = get_ble_sensor(config)

        self.assertIsNotNone(decoded, "No matching BLE advertisement received before timeout")
        self.assertIn("temperature_c", decoded)
        self.assertIn("humidity_pct", decoded)
        self.assertIn("battery_pct", decoded)
        self.assertGreaterEqual(decoded["battery_pct"], 0)
        self.assertLessEqual(decoded["battery_pct"], 100)
        self.assertGreater(decoded["humidity_pct"], 0)
        self.assertLessEqual(decoded["humidity_pct"], 100)
        self.assertGreater(decoded["temperature_c"], -40)
        self.assertLess(decoded["temperature_c"], 85)

