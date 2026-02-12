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


async def comprar(request):
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

    carteira = await carteira_repository.get_first_wallet()
    if not carteira:
        carteira = await carteira_repository.create_default_wallet()

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
    await carteira_repository.update_wallet(
        carteira["_id"],
        float(novo_saldo),
        criptos,
    )

    transacao = {
        "data_utc": datetime.utcnow().isoformat() + "Z",
        "tipo": "compra",
        "moeda": moeda_id,
        "quantidade": float(quantidade),
        "valor_reais": float(valor_reais),
        "preco_unitario_brl": float(preco_decimal),
    }
    await historico_repository.inserir_transacao(transacao)

    return {
        "mensagem": "Compra realizada com sucesso.",
        "moeda": moeda_id,
        "quantidade": float(quantidade),
        "valor_reais": float(valor_reais),
        "saldo_reais": float(novo_saldo),
    }