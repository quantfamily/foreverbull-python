from datetime import datetime

import pytest
from foreverbull.data.data import Database
from foreverbull.data.stock_data import Asset, Portfolio, Position, StockData
from sqlalchemy.orm import sessionmaker

date = datetime(2016, 1, 4, 21)


@pytest.fixture()
def sample_asset():
    return Asset(sid=1, symbol="KEB", asset_name="BERLINER KEBAP")


@pytest.fixture()
def sample_stock_data(sample_asset):
    return StockData(asset_id=sample_asset.sid)


@pytest.fixture()
def sample_portfolio():
    return Portfolio(
        session_id="test_session",
        cash_flow=123.2,
        starting_cash=1000,
        portfolio_value=2134.2,
        pnl=32.2,
        returns=22.2,
        start_date=date,
        current_date=date,
        positions_value=222.4,
        positions_exposure=100.0,
    )


@pytest.fixture()
def sample_position(sample_asset):
    return Position(asset_id=sample_asset.sid, amount=10, cost_basis=12.2, last_sale_price=77.4, last_sale_date=date)


@pytest.fixture()
def db():
    db = Database("test_session")
    db.connect()
    return db


@pytest.fixture()
def db_with_sample_data(db, sample_asset, sample_stock_data, sample_portfolio, sample_position):
    Session = sessionmaker(db.engine)

    with Session() as db_session:
        db_session.add(sample_asset)
        db_session.add(sample_stock_data)
        db_session.add(sample_portfolio)
        db_session.commit()
        db_session.refresh(sample_portfolio)

    with Session() as db_session:
        sample_position.portfolio_id = sample_portfolio.id
        db_session.add(sample_position)
        db_session.commit()

    return db
