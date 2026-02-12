from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.application.services import auth_service
from app.domain.models.schemas import UserSchema, LoginSchema
from app.infrastructure.security import oauth2_scheme


auth_router = APIRouter(prefix="/auth", tags=["autenticacao"])


@auth_router.post("/criar_conta")
async def criar_conta(user: UserSchema):
    return await auth_service.criar_conta(user)


@auth_router.post("/login")
async def login(login_data: LoginSchema):
    return await auth_service.login(login_data)


@auth_router.post("/login-form")
async def login_form(dados_forms: OAuth2PasswordRequestForm = Depends()):
    return await auth_service.login_form(dados_forms)


@auth_router.get("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    return await auth_service.refresh(token)