from fastapi import APIRouter, HTTPException, status, Depends

from app.infrastructure.integrations.coingecko import (
    buscar_preco_com_id,
    MoedaInvalidaError,
    MoedaNaoEncontradaError,
)
from app.infrastructure.db.database import carteiras_collection
from app.presentation.dependencies import verify_token


carteira_router = APIRouter(tags=["carteira"])


async def get_or_create_wallet():
    carteira = await carteiras_collection.find_one({})

    if not carteira:
        carteira = {"saldo_reais": 10000, "criptos": {}}
        await carteiras_collection.insert_one(carteira)

    return carteira


async def preco_atual(moeda: str) -> tuple[str, float]:
    try:
        return await buscar_preco_com_id(moeda)
    except MoedaInvalidaError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except MoedaNaoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Erro ao consultar a CoinGecko.",
        ) from exc


@carteira_router.get("/cotacao/{moeda}")
async def cotacao(moeda: str, usuario: dict = Depends(verify_token)):
    moeda_id, preco = await preco_atual(moeda)
    return {"moeda": moeda_id, "preco_brl": preco}


@carteira_router.get("/saldo")
async def ver_saldo(usuario: dict = Depends(verify_token)):
    carteira = await get_or_create_wallet()
    return {"saldo_reais": carteira["saldo_reais"], "criptomoedas": carteira["criptos"]}
