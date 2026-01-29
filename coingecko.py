import time
import httpx

BASE_URL = "https://api.coingecko.com/api/v3"
_CACHE_TTL_SECONDS = 600
_MOEDAS_CACHE = []
_MOEDAS_CACHE_TS = 0.0


def _normalizar(termo: str) -> str:
    return termo.lower().strip()


async def _listar_moedas():
    global _MOEDAS_CACHE, _MOEDAS_CACHE_TS

    agora = time.time()
    if _MOEDAS_CACHE and (agora - _MOEDAS_CACHE_TS) < _CACHE_TTL_SECONDS:
        return _MOEDAS_CACHE

    url = f"{BASE_URL}/coins/list"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)
        response.raise_for_status()

    _MOEDAS_CACHE = response.json()
    _MOEDAS_CACHE_TS = agora
    return _MOEDAS_CACHE


async def buscar_id_moeda(termo: str) -> str:
    termo = _normalizar(termo)
    if not termo:
        raise Exception("Moeda invalida")

    moedas = await _listar_moedas()

    for moeda in moedas:
        if moeda.get("id") == termo:
            return moeda["id"]

    for moeda in moedas:
        if moeda.get("symbol") == termo:
            return moeda["id"]

    for moeda in moedas:
        if _normalizar(moeda.get("name", "")) == termo:
            return moeda["id"]

    raise Exception("Moeda nao encontrada na CoinGecko")


async def buscar_preco_com_id(moeda: str) -> tuple[str, float]:
    moeda_id = await buscar_id_moeda(moeda)

    url = f"{BASE_URL}/simple/price"
    params = {"ids": moeda_id, "vs_currencies": "brl"}

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()

    data = response.json()

    if moeda_id not in data or "brl" not in data[moeda_id]:
        raise Exception("Moeda nao encontrada na CoinGecko")

    return moeda_id, data[moeda_id]["brl"]


async def buscar_preco(moeda: str) -> float:
    _, preco = await buscar_preco_com_id(moeda)
    return preco
