from fastapi import FastAPI

app = FastAPI()

from routes.carteira import carteira_router
from routes.compra import compra_router
from routes.venda import venda_router
from routes.historico import historico_router

app.include_router(carteira_router)
app.include_router(compra_router)
app.include_router(venda_router)
app.include_router(historico_router)


