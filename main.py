from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from passlib.context import CryptContext
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "50"))

app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login_form")

from routes.carteira import carteira_router
from routes.compra import compra_router
from routes.venda import venda_router
from routes.historico import historico_router
from routes.auth import auth_router

app.include_router(carteira_router)
app.include_router(compra_router)
app.include_router(venda_router)
app.include_router(historico_router)
app.include_router(auth_router)
