import foreverbull

bull = foreverbull.Foreverbull()

@bull.on("stock_data")
def ema(tick, database, ema_low=16, ema_high=32):
    pass
