import os
import unittest
from unittest.mock import patch

from eink_dashboard.config import load_config


class LoadConfigTests(unittest.TestCase):
    def test_reads_environment_overrides(self):
        env = {
            "EINK_CITY": "Warsaw",
            "EINK_LAT": "52.2297",
            "EINK_LON": "21.0122",
            "EINK_TIMEZONE": "Europe/Warsaw",
            "EINK_STOOQ_SYMBOLS": "cdr,cdr.pl",
            "EINK_BT_TARGET_NAME": "ATC_TEST",
            "EINK_BT_RETRY_DELAY_S": "5",
        }

        with patch.dict(os.environ, env, clear=False):
            config = load_config()

        self.assertEqual(config.location.city, "Warsaw")
        self.assertEqual(config.location.lat, 52.2297)
        self.assertEqual(config.location.lon, 21.0122)
        self.assertEqual(config.market.symbols, ("cdr", "cdr.pl"))
        self.assertEqual(config.ble.target_name, "ATC_TEST")
        self.assertEqual(config.ble.retry_delay_s, 5.0)

