from fastapi import APIRouter, Depends

from app.application.services.historico_service import listar
from app.presentation.dependencies import verify_token

historico_router = APIRouter(prefix="/historico", tags=["historico"])


@historico_router.get("")
async def read_history(usuario: dict = Depends(verify_token)):
    return await listar()