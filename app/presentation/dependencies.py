from fastapi import Depends, HTTPException
from jose import jwt, JWTError

from app.infrastructure.repositories import users_repository
from app.infrastructure.security import SECRET_KEY, ALGORITHM, oauth2_scheme


async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        dict_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = dict_info.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token invalido")

        usuario = await users_repository.find_by_username(username)
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario nao encontrado")

        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido")