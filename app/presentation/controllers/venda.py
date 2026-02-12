from fastapi import APIRouter, Depends

from app.application.services.venda_service import vender as vender_service
from app.domain.models.schemas import VendaRequest
from app.presentation.dependencies import verify_token

venda_router = APIRouter(prefix="/venda", tags=["venda"])


@venda_router.post("/vender")
async def vender(request: VendaRequest, usuario: dict = Depends(verify_token)):
    return await vender_service(request)
