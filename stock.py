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
buy_sell: +1 for buying; -1 for selling.
quantity: non-negative integer of shares traded.
trade_price: non-negative integer for stock's trade price.
trade_time: a datetime time stamp for the trade record.
"""


class Stock:
    """Super simple stock.

    Trades relevant to this stock are stored in a `semi-private' list
    attribute, _trades, each as namedtuple object.

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
    """

    # Static variables for the Stock class
    stocks = {}  # a dict to help with stock-wide calculations

    def __init__(self, symbol, stype, last_dividend, fixed_dividend,
                 par_value):
        """
        Initializes a stock.

        The (static) Stock.stocks dictionary is automatically updated with the
        new entry. The stock's symbol must be unique; if the symbol already
        exists, then the previous class instance with this symbol will be
        overwritten.
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

        # Add to the class dictionary. The stocks are uniquely identified by
        # their symbol.
        Stock.stocks[symbol] = self  # a reference to the stock instance

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

    def dividend_yield(self):
        """
        Return the stock's dividend yield.

        The calculation depends on the type of the stock.
        The ticker price is calculated from the stock's trading in the past 15
        minutes; if there have been no trades use the par value of the stock.
        """

        ticker_price = self.stock_price()

        # Force float division (standard in Python 3.x)
        if self.stype == 'common':
            return float(self.last_dividend) / ticker_price

        return float(self.fixed_dividend) * self.par_value / ticker_price

    def price_earnings_ratio(self):
        """
        Returns the stock's price-earnings ratio.

        The ticker price is calculated from the stock's trading in the past 15
        minutes; if there have been no trades use the par value of the stock.
        """

        ticker_price = self.stock_price()

        # Assume 'dividend' means 'last dividend' in the specification.
        # NOTE I am not familiar with these terms, so I may be wrong.
        return ticker_price / self.last_dividend  # force float division

    def buy(self, quantity, trade_price, trade_time=None):
        """
        Records a 'buy' trade.

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

        This is a convenience function, to present a nicer interface. The work
        is done by invoking the record_trade method.

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

        self._trades.append(Trade(buy_sell, quantity, trade_price, trade_time))

    def stock_price(self, time_window=datetime.timedelta(minutes=15)):
        """
        Calculate the (weighted) mean stock price in some time window relative
        to the current time.

        time_window : the length of the window in which to take the mean;
                      defaults to 15 minutes (before now).
        """

        # If there have been no stock trades at all, then return the par value
        # of the stock.
        if self._trades is False:
            return self.par_value

        # If we have any trades, we can attempt to calculate a mean.
        trade_value = 0
        trade_quantity = 0
        # Generate an iterable by selecting trades within the time window;
        # then, do a simple weighted mean calculation.
        for trade in filter(lambda trade: (datetime.datetime.now() -
                                           time_window <=
                                           trade.trade_time <=
                                           datetime.datetime.now()),
                            self._trades):
            trade_value += trade.trade_price * trade.quantity
            trade_quantity += trade.quantity

        if trade_quantity > 0:
            return float(trade_value) / trade_quantity  # force float division

        # If all trades happened before the specified time window, return
        # the par value.
        # NOTE This is not ideal. Perhaps a better implementation
        # would be to raise an exception and request a longer time window.
        return self.par_value

    @staticmethod
    def gbce_all_share_index():
        """
        Calculate a global index from the geometric mean of all stock prices.

        The stock prices used for this calculation are the ticker prices.
        """

        # Do the calculation in log space to avoid working with scary
        # exponents. If the ticker price is 0, we'll exclude that stock from
        # the geometric mean.
        log_sum = 0
        n_zeros = 0
        for _, stock in Stock.stocks.items():
            ticker_price = stock.stock_price()
            if ticker_price == 0:
                n_zeros += 1
                continue
            log_sum += log(ticker_price)

        # Cover the edge case of all zeros.
        if n_zeros == len(Stock.stocks):
            return 0.

        # Exponentiate the answer before returning.
        return exp((1. / (len(Stock.stocks)  - n_zeros)) * log_sum)
