from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from fastapi import HTTPException, status

from app.infrastructure.integrations.coingecko import (
    buscar_preco_com_id,
    MoedaInvalidaError,
    MoedaNaoEncontradaError,
)
from app.infrastructure.repositories import carteira_repository, historico_repository


def _to_decimal(valor: float | int) -> Decimal:
    return Decimal(str(valor))


def _quantize_8(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)


async def vender(request, username: str):
    try:
        moeda_id, preco = await buscar_preco_com_id(request.moeda)
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

    carteira = await carteira_repository.get_wallet_by_username(username)
    if not carteira:
        carteira = await carteira_repository.create_default_wallet(username)

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

    await carteira_repository.update_wallet(
        carteira["_id"],
        float(novo_saldo),
        criptos,
    )

    transacao = {
        "data_utc": datetime.utcnow().isoformat() + "Z",
        "username": username,
        "tipo": "venda",
        "moeda": moeda_id,
        "quantidade": float(quantidade),
        "valor_reais": float(valor_reais),
        "preco_unitario_brl": float(preco_decimal),
    }
    await historico_repository.inserir_transacao(transacao)

    return {
        "mensagem": "Venda realizada com sucesso.",
        "moeda": moeda_id,
        "quantidade": float(quantidade),
        "valor_reais": float(valor_reais),
        "saldo_reais": float(novo_saldo),
    }
