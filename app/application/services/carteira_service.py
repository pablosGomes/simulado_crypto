from fastapi import HTTPException, status

from app.infrastructure.integrations.coingecko import (
    buscar_preco_com_id,
    MoedaInvalidaError,
    MoedaNaoEncontradaError,
)
from app.infrastructure.repositories import carteira_repository


async def get_or_create_wallet(username: str):
    carteira = await carteira_repository.get_wallet_by_username(username)
    if not carteira:
        carteira = await carteira_repository.create_default_wallet(username)
    return carteira


async def obter_cotacao(moeda: str) -> tuple[str, float]:
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


async def obter_saldo(username: str):
    carteira = await get_or_create_wallet(username)
    return {"saldo_reais": carteira["saldo_reais"], "criptomoedas": carteira["criptos"]}
