from foreverbull.data.stock_data import Asset, Base, Portfolio, Position
from pandas import read_sql_query
from sqlalchemy import create_engine, desc
from sqlalchemy.orm.session import sessionmaker


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
        self.session_maker = sessionmaker(self.engine)

    def stock_data(self, symbol: str = None):
        if symbol:
            query = f"""Select asset_id, date, price, high, low, open, close, volume, last_traded
                        FROM end_of_day INNER JOIN asset ON end_of_day.asset_id = asset.id
                        WHERE end_of_day.session_id='{self.session_id}' AND asset.symbol='{symbol}'"""
        else:
            query = f"""Select asset_id, date, price, high, low, open, close, volume, last_traded
                        FROM end_of_day WHERE session_id='{self.session_id}'"""
        return read_sql_query(query, self.engine)

    def portfolio(self) -> Portfolio:
        with self.session_maker() as db_session:
            q = db_session.query(Portfolio).filter_by(session_id=self.session_id)
            portfolio = q.order_by(desc(Portfolio.current_date)).first()
        return portfolio

    def get_position(self, asset: Asset) -> Position:
        portfolio = self.portfolio()

        with self.session_maker() as db_session:
            query = db_session.query(Position).join(Portfolio).join(Asset)
            query = query.filter(Portfolio.id == portfolio.id)
            query = query.filter(Asset.sid == asset.sid)
            position = query.first()

        return position
