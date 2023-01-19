from typing import Union

import sqlalchemy.types as types
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, JSON
from sqlalchemy.orm import validates, relationship

from database import Base


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
    
    assessment = relationship("Assessment", back_populates="creator")
    student_answers = relationship("AnswerAssessment", back_populates="student")

    @validates('password')
    def validate_password(self, key, user_password) -> str:
        if len(user_password) < 8:
            raise ValueError("Password length must be greater than 7")
        return user_password

class TokenData(BaseModel):
    username: Union[str, None] = None

class Assessment(Base):
    __tablename__ = "assessment"
    id = Column(Integer, primary_key=True)
    subject_name = Column(String(25))
    date = Column(Date)
    time = Column(Time)
    questions = Column(JSON)

    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="assessment")

    assessment_answer = relationship("AnswerAssessment", back_populates="user_assessment")

class AnswerAssessment(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True)
    answers = Column(JSON)
    student_id = Column(Integer, ForeignKey("users.id"))
    user_assessment_id=Column(Integer, ForeignKey("assessment.id"))

    # represent which user submitted assessment.
    student = relationship("User", back_populates="student_answers")

    # # represent asnwer belongs to which assessment.
    user_assessment = relationship("Assessment", back_populates="assessment_answer")
