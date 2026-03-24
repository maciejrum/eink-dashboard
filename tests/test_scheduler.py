from datetime import datetime
import unittest

from eink_dashboard.scheduler import seconds_until_next_minute


class SchedulerTests(unittest.TestCase):
    def test_counts_until_next_minute(self):
        now = datetime(2026, 3, 18, 14, 10, 15)
        self.assertEqual(seconds_until_next_minute(now), 45)

    def test_counts_full_minute_when_on_minute_boundary(self):
        now = datetime(2026, 3, 18, 14, 40, 0)
        self.assertEqual(seconds_until_next_minute(now), 60)

    def test_rolls_over_midnight(self):
        now = datetime(2026, 3, 18, 23, 59, 50)
        self.assertEqual(seconds_until_next_minute(now), 10)
