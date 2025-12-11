from fastapi import HTTPException, status, Depends
from fastapi.security import APIKeyQuery
from settings import settings

api_key_scheme = APIKeyQuery(name="access_token")

def api_key_auth(access_token: str = Depends(api_key_scheme)):
    access_tokens = settings.access_tokens

    if access_token not in access_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden: Invalid accessToken")