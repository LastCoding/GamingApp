from sqlalchemy.sql.sqltypes import String
from sql_app.database import Base
from pydantic import BaseModel

class Post(BaseModel):

    name: str
    platforms: str
    genre: str