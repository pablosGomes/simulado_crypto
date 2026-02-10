from datetime import datetime
from decimal import Decimal, ROUND_DOWN

from fastapi import APIRouter, HTTPException, status, Depends

from app.domain.models.schemas import CompraRequest
from app.infrastructure.integrations.coingecko import (
    buscar_preco_com_id,
    MoedaInvalidaError,
    MoedaNaoEncontradaError,
)
from app.infrastructure.db.database import carteiras_collection, historico_collection
from app.presentation.dependencies import verify_token

compra_router = APIRouter(tags=["compra"])


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


def _to_decimal(valor: float | int) -> Decimal:
    return Decimal(str(valor))


def _quantize_8(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)


@compra_router.post("/comprar")
async def comprar(request: CompraRequest , usuario: dict = Depends(verify_token)):
    moeda_id, preco = await preco_atual(request.moeda)

    carteira = await get_or_create_wallet()
    saldo_reais = _to_decimal(carteira["saldo_reais"])
    valor_reais = _to_decimal(request.valor_reais)
    preco_decimal = _to_decimal(preco)

    if saldo_reais < valor_reais:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente em reais.",
        )

    quantidade = _quantize_8(valor_reais / preco_decimal)
    criptos = carteira.get("criptos", {})
    atual = _to_decimal(criptos.get(moeda_id, 0))
    criptos[moeda_id] = float(_quantize_8(atual + quantidade))

    novo_saldo = saldo_reais - valor_reais
    await carteiras_collection.update_one(
        {"_id": carteira["_id"]},
        {"$set": {"saldo_reais": float(novo_saldo), "criptos": criptos}},
    )

    transacao = {
        "data_utc": datetime.utcnow().isoformat() + "Z",
        "tipo": "compra",
        "moeda": moeda_id,
        "quantidade": float(quantidade),
        "valor_reais": float(valor_reais),
        "preco_unitario_brl": float(preco_decimal),
    }
    await historico_collection.insert_one(transacao)

    return {
        "mensagem": "Compra realizada com sucesso.",
        "moeda": moeda_id,
        "quantidade": float(quantidade),
        "valor_reais": float(valor_reais),
        "saldo_reais": float(novo_saldo),
    }
