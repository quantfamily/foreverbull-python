import foreverbull

bull = foreverbull.Foreverbull()

@bull.on("stock_data")
def sample_algo(tick, database, ma_low, ma_high):
    print("High", ma_low, flush=True)
    print("low", ma_high, flush=True)
