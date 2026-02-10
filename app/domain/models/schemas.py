from pydantic import BaseModel, Field
from typing import Optional


class CompraRequest(BaseModel):
    moeda: str = Field(..., min_length=1)
    valor_reais: float = Field(..., gt=0)

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


class VendaRequest(BaseModel):
    moeda: str = Field(..., min_length=1)
    quantidade: float = Field(..., gt=0)
