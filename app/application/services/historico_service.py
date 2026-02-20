from app.infrastructure.repositories import historico_repository


async def listar(username: str):
    return await historico_repository.listar_transacoes(username)
