import json
from typing import List, Optional

from pydantic import BaseModel


class Base(BaseModel):
    @classmethod
    def load(cls, data):
        if type(data) is dict:
            return cls.parse_obj(data)
        loaded = json.loads(data.decode())
        return cls.parse_obj(loaded)

    def dump(self):
        return self.json()


class Config(BaseModel):
    start_date: str = "2017-01-01"
    end_date: str = "2017-10-31"
    timezone: str = "utc"
    benchmark: str = "AAPL"
    assets: List[str] = ["AAPL", "TSLA"]


class Backtest(BaseModel):
    id: Optional[str]
    config: dict


class Service(BaseModel):
    id: Optional[int]
    name: str = "algo"
    description: str = "default"
    container_id: int = None


class Container(BaseModel):
    id: Optional[int]
    source: str = "dockerhub"
    image: str = "zipline-foreverbull-11"


class Session(BaseModel):
    id: Optional[int]
    backtest_id: Optional[int]
