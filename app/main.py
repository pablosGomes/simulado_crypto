from fastapi import FastAPI
from app.presentation.controllers.carteira import carteira_router
from app.presentation.controllers.compra import compra_router
from app.presentation.controllers.venda import venda_router
from app.presentation.controllers.historico import historico_router
from app.presentation.controllers.auth import auth_router

app = FastAPI()

app.include_router(carteira_router)
app.include_router(compra_router)
app.include_router(venda_router)
app.include_router(historico_router)
app.include_router(auth_router)
