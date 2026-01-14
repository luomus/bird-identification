from fastapi import HTTPException, status, Depends
from fastapi.security import APiKeyHeader
from scripts.settings import settings

api_key_scheme = APIKeyHeader(name="x-key")

def api_key_auth(access_key: str = Depends(api_key_scheme)):
    access_tokens = settings.access_tokens

    if access_key not in access_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden: Invalid accessToken")