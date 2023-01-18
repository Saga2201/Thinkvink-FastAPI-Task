from sqlalchemy import Column, Integer, String
from database import Base
import sqlalchemy.types as types
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.orm import validates
from pydantic import BaseModel
from typing import Union

def char_len(str):
    return len(str)
    
class UserType(types.TypeDecorator):
    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(UserType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.items() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True)
    email = Column(String(70))
    user_type = Column(UserType({"Student": "student", "Teacher": "teacher"}), nullable=False)
    password = Column('user_password', String(100), nullable=False)
    

    @validates('password')
    def validate_password(self, key, user_password) -> str:
        if len(user_password) < 8:
            raise ValueError("Password length must be greater than 7")
        return user_password

class TokenData(BaseModel):
    username: Union[str, None] = None