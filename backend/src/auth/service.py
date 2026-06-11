import hashlib
from core.database import get_db
from core.security import create_access_token
from .schemas import RegisterSchema, LoginSchema


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


async def register_user(data: dict) -> dict:
    schema = RegisterSchema(**data)
    db = await get_db()

    await db.execute(
        """
        INSERT INTO users (name, email, password_hash, tenant_id, role)
        VALUES ($1, $2, $3, $4, $5)
        """,
        schema.name,
        schema.email,
        hash_password(schema.password),
        schema.tenant_id,
        "consultant",
    )

    row = await db.fetchrow(
        "SELECT id, name, email, tenant_id, role FROM users WHERE email = $1",
        schema.email,
    )
    return dict(row)


async def login_user(data: dict) -> str:
    schema = LoginSchema(**data)
    db = await get_db()

    row = await db.fetchrow(
        "SELECT id, email, password_hash, tenant_id, role FROM users WHERE email = $1",
        schema.email,
    )
    if not row:
        raise ValueError("Credenciais inválidas")

    if hash_password(schema.password) != row["password_hash"]:
        raise ValueError("Credenciais inválidas")

    token = create_access_token(
        sub=row["email"],
        tenant_id=row["tenant_id"],
        role=row["role"],
    )
    return token
