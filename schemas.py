from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True