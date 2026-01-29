from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from db import carteiras_collection, historico_collection
from coingecko import buscar_preco_com_id

compra_router = APIRouter(tags=["compra"])


class CompraRequest(BaseModel):
    moeda: str = Field(..., min_length=1)
    valor_reais: float = Field(..., gt=0)


async def get_or_create_wallet():
    carteira = await carteiras_collection.find_one({})

    if not carteira:
        carteira = {"saldo_reais": 10000, "criptos": {}}
        await carteiras_collection.insert_one(carteira)

    return carteira


async def preco_atual(moeda: str) -> tuple[str, float]:
    try:
        return await buscar_preco_com_id(moeda)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@compra_router.post("/comprar")
async def comprar(request: CompraRequest):
    moeda_id, preco = await preco_atual(request.moeda)

    carteira = await get_or_create_wallet()
    saldo_reais = carteira["saldo_reais"]
    if saldo_reais < request.valor_reais:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente em reais.",
        )

    quantidade = request.valor_reais / preco
    criptos = carteira.get("criptos", {})
    criptos[moeda_id] = criptos.get(moeda_id, 0) + quantidade

    novo_saldo = saldo_reais - request.valor_reais
    await carteiras_collection.update_one(
        {"_id": carteira["_id"]},
        {"$set": {"saldo_reais": novo_saldo, "criptos": criptos}},
    )

    transacao = {
        "data_utc": datetime.utcnow().isoformat() + "Z",
        "tipo": "compra",
        "moeda": moeda_id,
        "quantidade": quantidade,
        "valor_reais": request.valor_reais,
        "preco_unitario_brl": preco,
    }
    await historico_collection.insert_one(transacao)

    return {
        "mensagem": "Compra realizada com sucesso.",
        "moeda": moeda_id,
        "quantidade": quantidade,
        "valor_reais": request.valor_reais,
        "saldo_reais": novo_saldo,
    }
