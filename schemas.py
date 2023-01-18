from pydantic import BaseModel

class User(BaseModel):
    email: str
    user_type: str
    password: str


class UserProfile(BaseModel):
    username: str
    email: str
    user_type: str
    password: str

class ChangePassword(BaseModel):
    new_password: str
    confirm_new_password: str