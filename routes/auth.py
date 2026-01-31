from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Depends
from jose import JWTError, jwt
from db import users_collection
from main import bcrypt_context, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme
from schemas import UserSchema, LoginSchema
from dependencies import verify_token


auth_router = APIRouter(prefix="/auth", tags=["autenticacao"])


def criar_token(id_usuario: str, duracao: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    data_expiracao = datetime.now(timezone.utc) + timedelta(minutes=duracao)
    to_encode = {"sub": id_usuario, "exp": data_expiracao}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def autenticar_usuario(username: str, password: str):
    usuario = await users_collection.find_one({"username": username})
    if not usuario:
        return None
    if not bcrypt_context.verify(password, usuario.get("password", "")):
        return None
    return usuario


@auth_router.post("/criar_conta")
async def criar_conta(user: UserSchema):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ja existe")

    senha_criptografada = bcrypt_context.hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = senha_criptografada
    await users_collection.insert_one(user_dict)
    return {"msg": "Usuario criado com sucesso"}


@auth_router.post("/login")
async def login(login_data: LoginSchema):
    user = await autenticar_usuario(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")

    access_token = criar_token(user["username"])
    refresh_token = criar_token(user["username"])
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@auth_router.post("/login-form")
async def login_form(dados_forms: OAuth2PasswordRequestForm = Depends()):
    user = await autenticar_usuario(dados_forms.username, dados_forms.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")
    
    else:
        access_token = criar_token(user["username"])
        return {"access_token": access_token , "token_type": "bearer"}

@auth_router.get("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    new_access_token = criar_token(username)
    new_refresh_token = criar_token(username)
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
