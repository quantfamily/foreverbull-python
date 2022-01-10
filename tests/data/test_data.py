import pandas
from foreverbull.data.data import Database
from foreverbull.data.stock_data import Asset, Portfolio, Position
from foreverbull_core.models.finance import Asset as AssetModel


def test_connect():
    db = Database(session_id="test_session", db_conf=None)
    db.connect()


def test_stock_data():
    db = Database(session_id="test_session", db_conf=None)
    db.connect()
    df = db.stock_data()
    assert type(df) == pandas.core.frame.DataFrame


def test_portfolio(db_with_sample_data: Database):
    portfolio = db_with_sample_data.portfolio()
    assert type(portfolio) == Portfolio


def test_get_position(db_with_sample_data: Database, sample_asset: Asset):
    model = AssetModel(sid=1, symbol="kebab", exchange="kebab")
    position = db_with_sample_data.get_position(model)

    assert type(position) == Position
