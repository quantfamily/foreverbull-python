from sqlalchemy import Column, Date, Integer, Numeric

from .data import Base


class StockData(Base):
    __tablename__ = "end_of_day"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer)
    session_id = Column(Integer)
    date = Column(Date)
    price = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    open = Column(Numeric)
    close = Column(Numeric)
    volume = Column(Integer)
    last_traded = Column(Date)
