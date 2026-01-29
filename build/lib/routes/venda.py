from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from coingecko import buscar_preco_com_id
from db import carteiras_collection, historico_collection

venda_router = APIRouter(tags=["venda"])


class VendaRequest(BaseModel):
    moeda: str = Field(..., min_length=1)
    quantidade: float = Field(..., gt=0)


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


@venda_router.post("/vender")
async def vender(request: VendaRequest):
    moeda_id, preco = await preco_atual(request.moeda)

    carteira = await get_or_create_wallet()
    criptos = carteira.get("criptos", {})
    disponivel = criptos.get(moeda_id, 0)
    if disponivel < request.quantidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade de criptomoeda insuficiente.",
        )

    valor_reais = request.quantidade * preco
    criptos[moeda_id] = disponivel - request.quantidade

    novo_saldo = carteira["saldo_reais"] + valor_reais
    await carteiras_collection.update_one(
        {"_id": carteira["_id"]},
        {"$set": {"saldo_reais": novo_saldo, "criptos": criptos}},
    )

    transacao = {
        "data_utc": datetime.utcnow().isoformat() + "Z",
        "tipo": "venda",
        "moeda": moeda_id,
        "quantidade": request.quantidade,
        "valor_reais": valor_reais,
        "preco_unitario_brl": preco,
    }
    await historico_collection.insert_one(transacao)

    return {
        "mensagem": "Venda realizada com sucesso.",
        "moeda": moeda_id,
        "quantidade": request.quantidade,
        "valor_reais": valor_reais,
        "saldo_reais": novo_saldo,
    }
