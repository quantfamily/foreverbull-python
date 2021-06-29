import pandas

from foreverbull.broker.data.data import Database


def test_connect():
    db = Database(session_id="1111", db_conf=None)
    db.connect()


def test_stock_data():
    db = Database(session_id="1111", db_conf=None)
    db.connect()
    df = db.stock_data()
    assert type(df) == pandas.core.frame.DataFrame
