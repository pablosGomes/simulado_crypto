from fastapi import APIRouter, Depends
from db import historico_collection
from dependencies import verify_token

historico_router = APIRouter(prefix="/historico", tags=["historico"])


@historico_router.get("")
async def read_history(usuario: dict = Depends(verify_token)):
    historico = []

    cursor = historico_collection.find().sort("data_utc", -1)

    async for transacao in cursor:
        transacao["_id"] = str(transacao["_id"])
        historico.append(transacao)

    return historico
