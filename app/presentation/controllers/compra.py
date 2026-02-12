from fastapi import APIRouter, Depends

from app.application.services.compra_service import comprar as comprar_service
from app.domain.models.schemas import CompraRequest
from app.presentation.dependencies import verify_token

compra_router = APIRouter(prefix="/compra", tags=["compra"])


@compra_router.post("/comprar")
async def comprar(request: CompraRequest, usuario: dict = Depends(verify_token)):
    return await comprar_service(request)
