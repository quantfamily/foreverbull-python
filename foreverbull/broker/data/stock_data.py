from sqlalchemy import Column, Integer, Numeric, Date


class StockData:
    __tablename__ = "end_of_day"
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
