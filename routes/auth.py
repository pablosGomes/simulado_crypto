from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext
from db import users_collection
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from schemas import UserSchema, LoginSchema
from main import bcrypt_context, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = APIRouter(prefix="/auth", tags=["autenticação"])

def criar_token(id_usuario: str):
    data_expiracao = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": id_usuario, "exp": data_expiracao}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def autenticar_usuario(username: str, password: str):
    user_data = users_collection.find_one({"username": username})
    if not user_data:
        return None
    bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if not bcrypt_context.verify(password, user_data["password"]):
        return None
    return UserSchema(**user_data)
    
@auth_router.post("/criar_conta")
async def criar_conta(user: UserSchema):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já existe")
    else:
        senha_criptografada = bcrypt_context.hash(user.password)
        user_dict = user.dict()
        user_dict["password"] = senha_criptografada
        await users_collection.insert_one(user_dict)
    return {"msg": "Usuário criado com sucesso"}

@auth_router.post("/login")
async def login(login_data: LoginSchema):
    user = autenticar_usuario(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    else:
        encoded_jwt = criar_token(str(user.username))

    return {"access_token": encoded_jwt, "token_type": "bearer"}

