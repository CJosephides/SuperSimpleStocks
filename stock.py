"""
stock.py

Implementation of the Stock class, for the Super Simple Stocks assignment.
"""

from collections import namedtuple
from math import nan
from math import log
from math import exp
import datetime

# Named tuple represents stock trades.
Trade = namedtuple('Trade', ['buy_sell', 'quantity', 'trade_price',
                             'trade_time'])
"""
buy_sell: +1 for buying; -1 for selling (enum-like)
quantity: non-negative integer of shares traded.
trade_price: non-negative integer for stock's trade price.
trade_time: a datetime time stamp for the trade record.
"""


class Stock:
    """
    Super simple stock.

    Attributes
    ----------
    symbol: alphabetic string indicating the shorthand name of the stock.
            Symbols uniquely identify each stock in a static dictionary.
    stype: a string in {'common', 'preferred'} indicating stock's type.
    last_dividend: a non-negative integer (in pennies) of the stock's last
                   dividend.
    fixed_dividend: a percentile in [0., 1.], or nan, of the stock's fixed
                    dividend.
    par_value: a non-negative integer (in pennies) of the stock's par value.
    _trades: trades relevant to this stock are stored in a `semi-private' list,
             each as namedtuple object.
    """

    def __init__(self, symbol, stype, last_dividend, fixed_dividend,
                 par_value):
        """
        Initializes a stock from input arguments, which must all be provided.
        """

        # Do a minimum amount of validation.
        assert symbol.isalpha(),\
            'stock symbol, %r,  is not alphabetic' % symbol
        assert stype.lower() in ('common', 'preferred'),\
            'stock type, %r, must be "common" or "preferred"' % stype
        assert (isinstance(last_dividend, int) and last_dividend >= 0),\
            ('stock last_dividend, %r, must be a non-negative integer'
             % last_dividend)
        assert (fixed_dividend is nan) or \
            (isinstance(fixed_dividend, float) and
             0. <= fixed_dividend <= 1.),\
            ('stock fixed dividend, %r, must be a valid percentile in '
             '[0., 1.] or nan' % fixed_dividend)
        assert (isinstance(par_value, int) and par_value >= 0),\
            'stock par_value, %r, must be a non-negative integer' % par_value

        self.symbol = symbol.upper()
        self.stype = stype.lower()
        self.last_dividend = last_dividend
        self.fixed_dividend = fixed_dividend
        self.par_value = par_value

        # Initialize a list of trades for this stock. We want this to be
        # semi-private and accessible by some interface instead, so we'll
        # underscore it.
        self._trades = []

    def __repr__(self):
        """
        This could be something more useful!
        """
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        """
        Print a simple summary of the stock.
        """
        return ('{0:s} ({1:s}): LastDiv: {2:d}, FixedDiv: {3:.2f}, '
                'ParVal: {4:d}'.format(self.symbol, self.stype,
                                       self.last_dividend, self.fixed_dividend,
                                       self.par_value))

    def buy(self, quantity, trade_price, trade_time=None):
        """
        Records a 'buy' trade.

        We explicitly forbid trades in the future (i.e. trade_time > now).

        This is a convenience function, to present a slightly nicer interface.
        The work is done by invoking the record_trade method.

        Args
        ----
        quantity : a non-negative integer.
        trade_price : a non-negative integer (in pennies).
        trade_time : a datetime object, which defaults to the current time.
        """

        if trade_time is None:
            trade_time = datetime.datetime.now()
        self._record_trade(1, quantity, trade_price, trade_time)

    def sell(self, quantity, trade_price, trade_time=None):
        """
        Records a 'sell' trade.

        We explicitly forbid trades in the future (i.e. trade_time > now).

        This is a convenience function, to present a nicer interface. The work
        is done by invoking the record_trade method.

        Args
        ----
        quantity : a non-negative integer.
        trade_price : a non-negative integer (in pennies).
        trade_time : a datetime object, which defaults to the current time.
        """

        if trade_time is None:
            trade_time = datetime.datetime.now()
        self._record_trade(-1, quantity, trade_price, trade_time)

    def _record_trade(self, buy_sell, quantity, trade_price, trade_time):
        """
        Records a buy or sell trade in the trade list.

        The Stock.buy and Stock.sell methods invoke this method.
        Trades are stored as a named tuple (one per trade).
        """

        # Do some validation.
        assert (isinstance(quantity, int) and quantity > 0),\
            'Trade quantity, %r, must be a non-negative integer' % quantity
        assert (isinstance(trade_price, int) and trade_price >= 0),\
            'Trade price, %r, must be a non-negative integer' % quantity
        assert isinstance(trade_time, datetime.datetime),\
            'Trade time, %r, must be a datetime object' % datetime
        assert trade_time <= datetime.datetime.now(),\
            'Trading time cannot be in the future!'

        self._trades.append(Trade(buy_sell, quantity, trade_price, trade_time))

    def stock_price(self, time_window=datetime.timedelta(minutes=15)):
        """
        Calculate the (weighted) mean stock price in some time window relative
        to the current time.

        Args:
        -----
        time_window : the length of the window in which to take the mean;
                      defaults to 15 minutes (before now).
        """

        # If there have been no stock trades at all, then return the par value
        # of the stock.
        if len(self._trades) == 0:
            return self.par_value

        # NOTE It is not clear how we should handle the case with no *recent*
        # trades. To handle this, I assumed that we should calculate an average
        # (over the specified time window length) starting from the time of the
        # *latest* trade and extending back. This is implemented below.

        latest_trade = max([trade.trade_time for trade in self._trades])

        # Check if we have had any trades in the specified time window.
        if datetime.datetime.now() - latest_trade <= time_window:
            # If we have recent trades, then we will extend the time window
            # backwards from the current time.
            search_start = datetime.datetime.now()
        else:
            # Otherwise, we will extend the time window backwards from the time
            # of the latest trade.
            search_start = latest_trade

        # Generate an iterable by selecting trades within the time window;
        # then, do a simple weighted mean calculation.
        trade_value = 0
        trade_quantity = 0
        for trade in filter(lambda trade: (search_start -
                                           time_window <=
                                           trade.trade_time <=
                                           search_start),
                            self._trades):
            trade_value += trade.trade_price * trade.quantity
            trade_quantity += trade.quantity

        return float(trade_value) / trade_quantity  # force float division

    def dividend_yield(self):
        """
        Return the stock's dividend yield.

        The calculation depends on the type of the stock.
        The ticker price is calculated from the stock's trading in the past 15
        minutes (by default). See Stock.stock_price() for details on how
        different cases (no trades, no recent trades, some recent trades) are
        handled.
        """

        ticker_price = self.stock_price()

        # Force float division (standard in Python 3.x)
        if self.stype == 'common':
            # Common stocks
            return float(self.last_dividend) / ticker_price
        # Preferred stocks
        return float(self.fixed_dividend) * self.par_value / ticker_price

    def price_earnings_ratio(self):
        """
        Returns the stock's price-earnings ratio.

        The ticker price is calculated from the stock's trading in the past 15
        minutes (by default). See Stock.stock_price() for details on how
        different cases (no trades, no recent trades, some recent trades) are
        handled.
        """

        ticker_price = self.stock_price()

        # We use the correct dividend calculation for each type of stock.
        if self.stype == 'common':
            # Common stocks use their last dividend.
            dividend = self.last_dividend
        else:
            # Preferred stocks use the product of fixed dividend and par value.
            dividend = self.fixed_dividend * self.par_value

        return ticker_price / dividend  # force float division


def gbce_all_share_index(stocks):
    """
    Calculate a global index from the geometric mean of all stock prices.

    The stock prices used for this calculation are the ticker prices.

    Args
    ----
    stocks: an array of Stock objects.

    Returns
    -------
    Geometric mean of all stocks.
    """

    # Do the calculation in log space to avoid working with scary
    # exponents. If the ticker price is 0, we'll exclude that stock from
    # the geometric mean.
    log_sum = 0
    n_zeros = 0
    for stock in stocks:
        ticker_price = stock.stock_price()
        if ticker_price == 0:
            n_zeros += 1
            continue
        log_sum += log(ticker_price)

    # Cover the edge case of all zeros.
    if n_zeros == len(stocks):
        return 0.

    # Exponentiate the answer before returning.
    return exp((1. / (len(stocks)  - n_zeros)) * log_sum)
