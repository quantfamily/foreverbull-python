import foreverbull

bull = foreverbull.Foreverbull()

@bull.on("stock_data")
def sample_algo(*args, **kwargs):
    pass
