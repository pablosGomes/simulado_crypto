from fastapi import HTTPException, status

from app.infrastructure.repositories import users_repository, carteira_repository
from app.infrastructure.security import (
    bcrypt_context,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone


def criar_token(id_usuario: str, duracao: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    data_expiracao = datetime.now(timezone.utc) + timedelta(minutes=duracao)
    to_encode = {"sub": id_usuario, "exp": data_expiracao}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def autenticar_usuario(username: str, password: str):
    usuario = await users_repository.find_by_username(username)
    if not usuario:
        return None
    if not bcrypt_context.verify(password, usuario.get("password", "")):
        return None
    return usuario


async def criar_conta(user):
    existing_user = await users_repository.find_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ja existe")

    senha_criptografada = bcrypt_context.hash(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = senha_criptografada
    await users_repository.insert_user(user_dict)
    carteira = await carteira_repository.get_wallet_by_username(user.username)
    if not carteira:
        await carteira_repository.create_default_wallet(user.username)
    return {"msg": "Usuario criado com sucesso"}


async def login(login_data):
    user = await autenticar_usuario(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")

    access_token = criar_token(user["username"])
    refresh_token = criar_token(user["username"])
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


async def login_form(dados_forms):
    user = await autenticar_usuario(dados_forms.username, dados_forms.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")

    access_token = criar_token(user["username"])
    return {"access_token": access_token, "token_type": "bearer"}


async def refresh(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

        new_access_token = criar_token(username)
        new_refresh_token = criar_token(username)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
