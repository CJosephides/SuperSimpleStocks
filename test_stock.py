"""
test_stock.py

Unit (and some not-so-unit) tests for stock.py.
"""

import datetime
from math import nan
import unittest
from stock import Stock

class StockTestCase(unittest.TestCase):
    """
    Tests for `stock.py`.
    """

    def test_stock_init(self):
        """
        Various Stock constructor calls to test attribute validation.
        """

        # Par values should not be negative.
        with self.assertRaises(AssertionError):
            Stock('TEA', 'common', 0, nan, -14)
        # Fixed dividend should not be an integer.
        with self.assertRaises(AssertionError):
            Stock('TEA', 'common', 0, 52, 100)
        # Fixed dividend should not be > 1.
        with self.assertRaises(AssertionError):
            Stock('TEA', 'common', 0, 1.01, 100)
        # Last dividend should not be negative.
        with self.assertRaises(AssertionError):
            Stock('TEA', 'common', -41, nan, 100)
        # Last dividend should not be a float.
        with self.assertRaises(AssertionError):
            Stock('TEA', 'common', 123.52, nan, 100)
        # Stock type should only be `common` or `preferred`.
        with self.assertRaises(AssertionError):
            Stock('TEA', 'best_stock', 100, nan, 100)
        # Stock symbol should not be an alphanumeric string.
        with self.assertRaises(AssertionError):
            Stock('a2vn52', 'common', 0, nan, 100)

        # The following should be constructed as valid Stock objects.
        self.assertIsInstance(Stock('TEA', 'common', 0, nan, 100), Stock)
        self.assertIsInstance(Stock('POP', 'common', 8, nan, 100), Stock)
        self.assertIsInstance(Stock('ALE', 'common', 23, nan, 60), Stock)
        self.assertIsInstance(Stock('GIN', 'preferred', 8, 0.02, 100), Stock)
        self.assertIsInstance(Stock('JOE', 'common', 13, nan, 250), Stock)

    def test_stock_buy_sell(self):
        """
        Test buying and selling stocks.
        """

        # Make a mock object for testing.
        # NOTE there are better ways to do this!
        sALE = Stock('ALE', 'common', 23, nan, 60)

        # Trade price should not be a string.
        with self.assertRaises(AssertionError):
            sALE.buy(500, 55, '2017 06 05 13 42 00')
        # Trade price should not be negative.
        with self.assertRaises(AssertionError):
            sALE.buy(500, -23)
        # Trade price should not be a float.
        with self.assertRaises(AssertionError):
            sALE.buy(500, 123.0)
        # Trade price should not be a string.
        with self.assertRaises(AssertionError):
            sALE.sell(500, 55, '2017 06 05 13 42 00')
        # Trade price should not be negative.
        with self.assertRaises(AssertionError):
            sALE.sell(500, -23)
        # Trade price should not be a float.
        with self.assertRaises(AssertionError):
            sALE.sell(500, 123.0)

        # `Buy` records should have a `+1` number in the buy_sell tuple record.
        sALE.buy(500, 25)
        self.assertEqual(sALE._trades[-1].buy_sell, 1)
        # `Sell` records should have a `-1` number in the buy_sell tuple record.
        sALE.sell(300, 15)
        self.assertEqual(sALE._trades[-1].buy_sell, -1)

        # Trading cannot happen in the future.
        with self.assertRaises(AssertionError):
            sALE.buy(500, 25,
                     datetime.datetime.now() + datetime.timedelta(minutes=1))

    def test_stock_price(self):
        """
        Tests stock (ticker) price calculation.
        """

        # Make a mock object for testing.
        sALE = Stock('ALE', 'common', 23, nan, 60)

        # A stock without trades has a ticker price equal to its par value.
        self.assertEqual(sALE.stock_price(), 60)

        # Add some mock Trades.
        sALE.buy(500, 25)
        sALE.sell(300, 15)
        self.assertEqual(len(sALE._trades), 2)

        # Easy case for ticker price with two Trades.
        self.assertEqual(sALE.stock_price(), ((500*25)+(300*15))/(500+300))

        # Add some mock Trades in the distant past (such that they are excluded
        # from the average).
        sALE.buy(100, 87, datetime.datetime.now() -
                 datetime.timedelta(minutes=16))
        sALE.buy(23, 34, datetime.datetime.now() -
                 datetime.timedelta(minutes=15))
        self.assertEqual(len(sALE._trades), 4)

        # Stock price should be unchanged.
        self.assertEqual(sALE.stock_price(), ((500*25)+(300*15))/(500+300))

    def test_stock_dividend_yield_common(self):
        """
        Tests correct dividend yield calculation for `common` stock types.
        """

        # Make a mock object for testing.
        sALE = Stock('ALE', 'common', 23, nan, 60)

        # A stock without trades has a default ticker price equal to its par
        # value.
        self.assertEqual(sALE.dividend_yield(), 23. / 60)

        # Add some mock Trades.
        sALE.buy(500, 25)
        sALE.sell(300, 15)
        self.assertEqual(len(sALE._trades), 2)

        # The dividend yield calculation should now use a ticker price
        # determined from the average trading price.
        self.assertEqual(sALE.dividend_yield(), 23. /
                         (((500*25)+(300*15))/(500+300)))

    def test_stock_dividend_yield_preferred(self):
        """
        Tests correct dividend yield calculation for `preferred` stock types.
        """

        # Make a mock object for testing.
        sGIN = Stock('GIN', 'preferred', 8, 0.02, 100)

        # A stock without trades has a default ticker price equal to its par
        # value. In this case, `preferred` stock types should have a price
        # earnings ratio equal to their par value.
        self.assertEqual(sGIN.dividend_yield(), 0.02)

        # Add some mock Trades.
        sGIN.buy(320, 95)
        sGIN.sell(180, 110)
        self.assertEqual(len(sGIN._trades), 2)

        # `preferred` stocks should not use the `common` calculation for
        # dividend yields...
        self.assertNotEqual(sGIN.dividend_yield(),
                            8 / ((320*95 + 180*110) / (320+180)))

        # ... instead, they should use the `preferred` calculation.
        self.assertEqual(sGIN.dividend_yield(),
                         (0.02 * 100) / ((320*95 + 180*110) / (320+180)))

    def test_stock_price_earnings_ratio(self):
        """
        Tests correct price-earnings calculation for both `common` and
        `preferred` stock types.
        """

        # Make a mock object for testing.
        sALE = Stock('ALE', 'common', 23, nan, 60)
        # Add some mock Trades.
        sALE.buy(500, 25)
        sALE.sell(300, 15)
        self.assertEqual(len(sALE._trades), 2)
        # Make a mock object for testing.
        sGIN = Stock('GIN', 'preferred', 8, 0.02, 100)
        # Add some mock Trades.
        sGIN.buy(320, 95)
        sGIN.sell(180, 110)
        self.assertEqual(len(sGIN._trades), 2)

        # `ALE` stock should use the last_dividend as dividend
        self.assertEqual(sALE.price_earnings_ratio(),
                         ((500*25+300*15)/(500+300)) / 23.)

        # But `GIN` stock should the fixed_dividend * par_value as dividend
        self.assertEqual(sGIN.price_earnings_ratio(),
                         ((320*95+180*110)/(320+180)) / (0.02 * 100))

    def test_gbce_all_share_index(self):
        """
        Test the GBCE All Share Index across multiple stocks, each with many
        trades.
        """

        # Create some mock Stocks and Trades for each.
        Stock('TEA', 'common', 0, nan, 100)
        Stock('POP', 'common', 8, nan, 100)
        Stock('ALE', 'common', 23, nan, 60)
        Stock('GIN', 'preferred', 8, 0.02, 100)
        Stock('JOE', 'common', 13, nan, 250)
        self.assertEqual(len(Stock.stocks), 5)

        # Add some Trades.
        trades = {
            'TEA': [(1, 10, 95, datetime.datetime.now()),
                    (-1, 20, 90, datetime.datetime.now()),
                    (1, 45, 120, datetime.datetime.now())],
            'POP': [(1, 90, 95, datetime.datetime.now()),
                    (1, 65, 90, datetime.datetime.now()),
                    (-1, 200, 100, datetime.datetime.now())],
            'ALE': [(1, 35, 50, datetime.datetime.now()),
                    (-1, 50, 10, datetime.datetime.now())],
            'GIN': [(1, 100, 1000, datetime.datetime.now() -
                     datetime.timedelta(minutes=14))]
        }

        for stock, trade_list in trades.items():
            for trade in trade_list:
                Stock.stocks[stock]._record_trade(*trade)

        # Check that the stock (ticker) price for each stock is correct.
        self.assertEqual(Stock.stocks['TEA'].stock_price(),
                         (10*95 + 20*90 + 45*120)/(10+20+45))
        self.assertEqual(Stock.stocks['POP'].stock_price(),
                         (90*95 + 65*90 + 200*100)/(90+65+200))
        self.assertEqual(Stock.stocks['ALE'].stock_price(),
                         (35*50 + 50*10)/(35+50))
        self.assertEqual(Stock.stocks['GIN'].stock_price(), 1000)
        self.assertEqual(Stock.stocks['JOE'].stock_price(),
                         Stock.stocks['JOE'].par_value)  # zero recorded trades

        # The geometric mean calculation should be correct.
        # We do this calculation in log space in Stock.gbce_all_share_index(),
        # so check against a calculation  without the transformation here.
        stock_price = [(10*95 + 20*90 + 45*120)/(10+20+45),
                       (90*95 + 65*90 + 200*100)/(90+65+200),
                       (35*50 + 50 * 10)/(35+50),
                       1000,
                       Stock.stocks['JOE'].par_value]

        self.assertAlmostEqual(Stock.gbce_all_share_index(),
                               (stock_price[0] * stock_price[1] *
                                stock_price[2] * stock_price[3] *
                                stock_price[4]) ** (1./5))

if __name__ == '__main__':
    unittest.main()
