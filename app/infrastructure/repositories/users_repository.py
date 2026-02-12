from app.infrastructure.db.database import users_collection


async def find_by_username(username: str):
    return await users_collection.find_one({"username": username})


async def insert_user(user_dict: dict):
    await users_collection.insert_one(user_dict)