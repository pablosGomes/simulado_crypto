from fastapi import APIRouter, HTTPException, status

from coingecko import buscar_preco
from db import carteiras_collection

carteira_router = APIRouter(tags=["carteira"])


async def get_or_create_wallet():
    carteira = await carteiras_collection.find_one({})

    if not carteira:
        carteira = {"saldo_reais": 10000, "criptos": {}}
        await carteiras_collection.insert_one(carteira)

    return carteira


async def preco_atual(moeda: str) -> float:
    try:
        return await buscar_preco(moeda)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@carteira_router.get("/cotacao/{moeda}")
async def cotacao(moeda: str):
    preco = await preco_atual(moeda)
    return {"moeda": moeda, "preco_brl": preco}


@carteira_router.get("/saldo")
async def ver_saldo():
    carteira = await get_or_create_wallet()
    return {"saldo_reais": carteira["saldo_reais"], "criptomoedas": carteira["criptos"]}
