from datetime import datetime
from decimal import Decimal, ROUND_DOWN

from fastapi import APIRouter, HTTPException, status, Depends

from app.domain.models.schemas import VendaRequest
from app.infrastructure.integrations.coingecko import (
    buscar_preco_com_id,
    MoedaInvalidaError,
    MoedaNaoEncontradaError,
)
from app.infrastructure.db.database import carteiras_collection, historico_collection
from app.presentation.dependencies import verify_token

venda_router = APIRouter(tags=["venda"])


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


@venda_router.post("/vender")
async def vender(request: VendaRequest, usuario: dict = Depends(verify_token)):
    moeda_id, preco = await preco_atual(request.moeda)

    carteira = await get_or_create_wallet()
    criptos = carteira.get("criptos", {})

    disponivel = _to_decimal(criptos.get(moeda_id, 0))
    quantidade = _quantize_8(_to_decimal(request.quantidade))
    if disponivel < quantidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade de criptomoeda insuficiente.",
        )

    preco_decimal = _to_decimal(preco)
    valor_reais = _quantize_8(quantidade * preco_decimal)

    criptos[moeda_id] = float(_quantize_8(disponivel - quantidade))

    saldo_atual = _to_decimal(carteira["saldo_reais"])
    novo_saldo = saldo_atual + valor_reais
    await carteiras_collection.update_one(
        {"_id": carteira["_id"]},
        {"$set": {"saldo_reais": float(novo_saldo), "criptos": criptos}},
    )

    transacao = {
        "data_utc": datetime.utcnow().isoformat() + "Z",
        "tipo": "venda",
        "moeda": moeda_id,
        "quantidade": float(quantidade),
        "valor_reais": float(valor_reais),
        "preco_unitario_brl": float(preco_decimal),
    }
    await historico_collection.insert_one(transacao)

    return {
        "mensagem": "Venda realizada com sucesso.",
        "moeda": moeda_id,
        "quantidade": float(quantidade),
        "valor_reais": float(valor_reais),
        "saldo_reais": float(novo_saldo),
    }
