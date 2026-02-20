from app.infrastructure.db.database import historico_collection


async def inserir_transacao(transacao: dict):
    await historico_collection.insert_one(transacao)


async def listar_transacoes(username: str):
    cursor = historico_collection.find({"username": username}).sort("data_utc", -1)
    transacoes = []
    async for transacao in cursor:
        transacao["_id"] = str(transacao["_id"])
        transacoes.append(transacao)
    return transacoes
