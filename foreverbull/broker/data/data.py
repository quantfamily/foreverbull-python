from sqlalchemy.orm import declarative_base

from sqlalchemy import create_engine
from pandas import read_sql_query


Base = declarative_base()


class Database:
    def __init__(self, hostname, port, db_name, user, password, session_id, **kwargs):
        self.uri = f"postgresql://{user}:{password}@{hostname}:{port}"
        print(self.uri)
        self.session_id = session_id

    def connect(self):
        self.engine = create_engine(self.uri)

    def stock_data(self):
        query = f"""Select asset_id, date, price, high, low, open, close, volume, last_traded
                    FROM end_of_day WHERE session_id={self.session_id}"""
        return read_sql_query(query, self.engine)
