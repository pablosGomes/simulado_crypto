from fastapi import APIRouter, Depends

from app.application.services.carteira_service import obter_cotacao, obter_saldo
from app.presentation.dependencies import verify_token

carteira_router = APIRouter(prefix="/carteira", tags=["carteira"])


@carteira_router.get("/cotacao/{moeda}")
async def cotacao(moeda: str, usuario: dict = Depends(verify_token)):
    moeda_id, preco = await obter_cotacao(moeda)
    return {"moeda": moeda_id, "preco_brl": preco}


@carteira_router.get("/saldo")
async def ver_saldo(usuario: dict = Depends(verify_token)):
    return await obter_saldo(usuario["username"])
