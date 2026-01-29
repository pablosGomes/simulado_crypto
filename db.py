from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URL)

db = client["crypto_simulador"]

carteiras_collection = db["carteiras"]
historico_collection = db["historico_transacoes"]
users_collection = db["users"]

