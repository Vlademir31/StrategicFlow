import jwt
from datetime import datetime, timedelta
from core.config import settings


def create_access_token(sub: str, tenant_id: str, role:
str) -> str:
    payload = {
        "sub": sub,
        "tenant_id": tenant_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, settings.JWT_SECRET,
algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET,
algorithms=[settings.JWT_ALGORITHM])
