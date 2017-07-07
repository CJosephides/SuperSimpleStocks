import datetime
from math import nan

# Valid stocks (assume ticker price equals par value)
Stock('TEA', 'common', 0, nan, 100, 100)
Stock('POP', 'common', 8, nan, 100, 100)
Stock('ALE', 'common', 23, nan, 60, 60)
Stock('GIN', 'preferred', 8, 0.02, 100, 100)
Stock('JOE', 'common', 13, nan, 250, 250)

# Add some trades for a stock.
Stock.stocks['TEA'].buy(10, 95, datetime.datetime.now() - datetime.timedelta(minutes=-30)
Stock.stocks['TEA'].sell(12, 104, datetime.datetime.now() - datetime.timedelta(minutes=-25)
Stock.stocks['TEA'].buy(24, 82, datetime.datetime.now() - datetime.timedelta(minutes=-15)
Stock.stocks['TEA'].sell(25, 99, datetime.datetime.now() - datetime.timedelta(minutes=-10)
Stock.stocks['TEA'].buy(82, 72, datetime.datetime.now() - datetime.timedelta(minutes=-5)
Stock.stocks['TEA'].sell(129, 92, datetime.datetime.now() - datetime.timedelta(minutes=-5)
