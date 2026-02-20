from app.infrastructure.db.database import carteiras_collection


async def get_wallet_by_username(username: str):
    return await carteiras_collection.find_one({"username": username})


async def create_default_wallet(username: str):
    carteira = {"username": username, "saldo_reais": 10000, "criptos": {}}
    result = await carteiras_collection.insert_one(carteira)
    carteira["_id"] = result.inserted_id
    return carteira


async def update_wallet(carteira_id, saldo_reais: float, criptos: dict):
    await carteiras_collection.update_one(
        {"_id": carteira_id},
        {"$set": {"saldo_reais": saldo_reais, "criptos": criptos}},
    )
