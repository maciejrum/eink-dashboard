from datetime import datetime
import unittest

from eink_dashboard.scheduler import seconds_until_next_half_hour


class SchedulerTests(unittest.TestCase):
    def test_counts_until_half_hour(self):
        now = datetime(2026, 3, 18, 14, 10, 0)
        self.assertEqual(seconds_until_next_half_hour(now), 20 * 60)

    def test_counts_until_next_full_hour(self):
        now = datetime(2026, 3, 18, 14, 40, 0)
        self.assertEqual(seconds_until_next_half_hour(now), 20 * 60)

    def test_rolls_over_midnight(self):
        now = datetime(2026, 3, 18, 23, 50, 0)
        self.assertEqual(seconds_until_next_half_hour(now), 10 * 60)

