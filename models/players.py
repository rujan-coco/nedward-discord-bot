import sqlmodel

engine = sqlmodel.create_engine('sqlite:///nedward.db')

class Players(sqlmodel.SQLModel, table=True):
  tag: str = sqlmodel.Field(primary_key=True, index=True)
  name: str
  townHallLevel: int
  role: str



