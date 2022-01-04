from foreverbull_core.models.finance import EndOfDay, Order
from foreverbull.data.data import Database
import foreverbull
import logging
import numpy
from talib import EMA

bull = foreverbull.Foreverbull()

logger = logging.getLogger(__name__)

@bull.on("stock_data")
def ema(tick: EndOfDay, database: Database, ema_low=16, ema_high=32):
    history = database.stock_data(tick.asset.symbol)
    high = EMA(history.price, timeperiod=ema_high)
    try:
        if numpy.isnan(high.iloc[-1]):
            return
        low = EMA(history.price, timeperiod=ema_low)
        if high.iloc[-1] < low.iloc[-1]:
            return Order(asset=tick.asset, amount=1)
        else:
            return Order(asset=tick.asset, amount=-1)
    except Exception as e:
        print("is exec: ", e)
