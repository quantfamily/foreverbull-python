import pandas

from sqlalchemy import create_engine

uri = "postgresql://postgres:1234@127.0.0.1:5432/"

engine = create_engine(uri)

query = f"""Select asset_id, date, price, high, low, open, close, volume, last_traded FROM end_of_day
            WHERE session_id=60"""

df = pandas.read_sql_query(query, engine)