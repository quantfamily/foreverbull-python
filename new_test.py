import foreverbull

backtest = foreverbull.backtest.Backtest()


@backtest.on("stock_data")
def take_stock_data(stock_data, data):
    print("HERE", stock_data)

    data.stock_data()


if __name__ == "__main__":
    backtest.run()
