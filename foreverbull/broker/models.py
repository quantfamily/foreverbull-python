from pydantic import BaseModel
import json


class Base(BaseModel):
    @classmethod
    def load(cls, data):
        if type(data) is dict:
            return cls.parse_obj(data)
        loaded = json.loads(data.decode())
        return cls.parse_obj(loaded)

    def dump(self):
        return self.json()


class Database(BaseModel):
    user: str
    password: str
    hostname: str
    port: int
    db_name: str


class Initialization(BaseModel):
    session_id: str
    database: Database
