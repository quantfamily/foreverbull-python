from sqlalchemy.orm import declarative_base

from sqlalchemy import create_engine
from pandas import read_sql_query


Base = declarative_base()


class Database:
    def __init__(self, session_id, db_conf=None):
        self.db_conf = db_conf
        if db_conf is None:
            self.uri = "sqlite:///:memory:"
        else:
            self.uri = f"{db_conf.dialect}://{db_conf.user}:{db_conf.password}@{db_conf.hostname}:{db_conf.port}"
        self.session_id = session_id

    def connect(self):
        self.engine = create_engine(self.uri)
        if self.db_conf is None:
            print("Creating")
            Base.metadata.create_all(self.engine)
            print("Tables: ", Base.metadata.tables.keys())

    def stock_data(self):
        query = f"""Select asset_id, date, price, high, low, open, close, volume, last_traded
                    FROM end_of_day WHERE session_id={self.session_id}"""
        return read_sql_query(query, self.engine)
