from sqlalchemy import Column, Date, Float, Integer, Numeric, String
from sqlalchemy.orm import declarative_base, relation
from sqlalchemy.sql.schema import ForeignKey

Base = declarative_base()


class Asset(Base):
    __tablename__ = "asset"
    sid = Column("id", Integer, primary_key=True)
    symbol = Column("symbol", String)
    asset_name = Column("name", String)
    exchange = Column("exchange", String)
    exchange_full = Column("exchange_full", String)
    country_code = Column("country_code", String)


class StockData(Base):
    __tablename__ = "end_of_day"
    id = Column("id", Integer, primary_key=True)
    asset_id = Column("asset_id", Integer, ForeignKey("asset.id"))
    asset = relation("Asset")
    session_id = Column("session_id", String)
    date = Column("date", Date)
    price = Column("price", Numeric)
    high = Column("high", Numeric)
    low = Column("low", Numeric)
    open = Column("open", Numeric)
    close = Column("close", Numeric)
    volume = Column("volume", Integer)
    last_traded = Column("last_traded", Date)


class Position(Base):
    __tablename__ = "asset_position"
    id = Column("id", Integer, primary_key=True)
    asset_id = Column("asset_id", Integer, ForeignKey("asset.id"))
    asset = relation("Asset")
    portfolio_id = Column("portfolio_id", Integer, ForeignKey("portfolio.id"))
    portfolio = relation("Portfolio", back_populates="positions")
    amount = Column("amount", Integer)
    cost_basis = Column("cost_basis", Float)
    last_sale_price = Column("last_sale_price", Float)
    last_sale_date = Column("last_sale_date", Date)


class Portfolio(Base):
    __tablename__ = "portfolio"
    id = Column("id", Integer, primary_key=True)
    session_id = Column("session_id", String)
    cash_flow = Column("cash_flow", Float)
    starting_cash = Column("starting_cash", Integer)
    portfolio_value = Column("portfolio_value", Float)
    pnl = Column("pnl", Float)
    returns = Column("_returns", Float)
    start_date = Column("start_date", Date)
    current_date = Column("_current_date", Date)
    positions_value = Column("positions_value", Float)
    positions_exposure = Column("positions_exposure", Float)
    positions = relation("Position", back_populates="portfolio")
