from app.infrastructure.db.database import carteiras_collection


async def get_first_wallet():
    return await carteiras_collection.find_one({})


async def create_default_wallet():
    carteira = {"saldo_reais": 10000, "criptos": {}}
    await carteiras_collection.insert_one(carteira)
    return carteira


async def update_wallet(carteira_id, saldo_reais: float, criptos: dict):
    await carteiras_collection.update_one(
        {"_id": carteira_id},
        {"$set": {"saldo_reais": saldo_reais, "criptos": criptos}},
    )