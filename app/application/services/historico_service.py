from app.infrastructure.repositories import historico_repository


async def listar():
    return await historico_repository.listar_transacoes()