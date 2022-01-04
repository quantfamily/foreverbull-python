from pandas import read_sql_query
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Database:
    def __init__(self, session_id, db_conf=None):
        self.db_conf = db_conf
        if db_conf is None:
            self.uri = "sqlite:///:memory:"
        else:
            self.uri = f"postgresql://{db_conf.user}:{db_conf.password}@127.0.0.1:{db_conf.port}/{db_conf.dbname}"
        self.session_id = session_id

    def connect(self):
        self.engine = create_engine(self.uri)
        if self.db_conf is None:
            Base.metadata.create_all(self.engine)

    def stock_data(self, symbol: str = None):
        if symbol:
            query = f"""Select asset_id, date, price, high, low, open, close, volume, last_traded
                        FROM end_of_day INNER JOIN asset ON end_of_day.asset_id = asset.id
                        WHERE end_of_day.session_id='{self.session_id}' AND asset.symbol='{symbol}'"""
        else:
            query = f"""Select asset_id, date, price, high, low, open, close, volume, last_traded
                        FROM end_of_day WHERE session_id='{self.session_id}'"""
        return read_sql_query(query, self.engine)
