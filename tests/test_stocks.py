import unittest

from eink_dashboard.providers.stocks import parse_stooq_quote


class ParseStooqQuoteTests(unittest.TestCase):
    def test_parses_valid_csv(self):
        csv_text = "Symbol,Date,Time,Open,High,Low,Close,Volume\nBMC,2026-03-18,12:00,1,2,3,4.56,789\n"

        quote = parse_stooq_quote(csv_text)

        self.assertEqual(quote["symbol"], "BMC")
        self.assertEqual(quote["date"], "2026-03-18")
        self.assertEqual(quote["time"], "12:00")
        self.assertEqual(quote["close"], 4.56)
        self.assertEqual(quote["currency"], "PLN")

    def test_returns_none_for_invalid_close(self):
        csv_text = "Symbol,Date,Time,Open,High,Low,Close,Volume\nBMC,2026-03-18,12:00,1,2,3,not-a-number,789\n"
        self.assertIsNone(parse_stooq_quote(csv_text))

