from sqlalchemy import Column, Date, Float, Integer, Numeric, String
from sqlalchemy.orm import declarative_base, relation
from sqlalchemy.sql.schema import ForeignKey

Base = declarative_base()


class Asset(Base):
    __tablename__ = "asset"
    sid = Column(Integer, primary_key=True)
    symbol = Column(String)
    asset_name = Column(String)
    exchange = Column(String)
    exchange_full = Column(String)
    country_code = Column(String)


class StockData(Base):
    __tablename__ = "end_of_day"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("asset.sid"))
    asset = relation("Asset")
    session_id = Column(String)
    date = Column(Date)
    price = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    open = Column(Numeric)
    close = Column(Numeric)
    volume = Column(Integer)
    last_traded = Column(Date)


class Position(Base):
    __tablename__ = "asset_position"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("asset.sid"))
    asset = relation("Asset")
    portfolio_id = Column(Integer, ForeignKey("portfolio.id"))
    portfolio = relation("Portfolio", back_populates="positions")
    amount = Column(Integer)
    cost_basis = Column(Float)
    last_sale_price = Column(Float)
    last_sale_date = Column(Date)


class Portfolio(Base):
    __tablename__ = "portfolio"
    id = Column(Integer, primary_key=True)
    session_id = Column(String)
    cash_flow = Column(Float)
    starting_cash = Column("starting_cash", Integer)
    portfolio_value = Column("portfolio_value", Float)
    pnl = Column("pnl", Float)
    returns = Column("_returns", Float)
    cash = Column("cash", Float)
    start_date = Column("start_date", Date)
    current_date = Column("_current_date", Date)
    positions_value = Column("positions_value", Float)
    positions_exposure = Column("positions_exposure", Float)
    positions = relation("Position", back_populates="portfolio")

    def get_position(self, asset: Asset) -> Position:
        for position in self.positions:
            if position.asset.symbol == asset.symbol:
                return position
        return None
