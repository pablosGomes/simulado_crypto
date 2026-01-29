from fastapi import APIRouter
from db import historico_collection

historico_router = APIRouter(prefix="/historico", tags=["historico"])


@historico_router.get("")
async def read_history():
    historico = []

    cursor = historico_collection.find().sort("data_utc", -1)

    async for transacao in cursor:
        transacao["_id"] = str(transacao["_id"])
        historico.append(transacao)

    return historico
