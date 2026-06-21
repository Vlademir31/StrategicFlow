import bcrypt
from core.database import get_db
from core.security import create_access_token
from .schemas import RegisterSchema, LoginSchema

def hash_password(password: str) -> str:
    """Gera um hash seguro com salgamento automático"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def register_user(data: dict) -> dict:
    schema = RegisterSchema(**data)
    db = await get_db()

    query_insert = """
        INSERT INTO users (name, email, password_hash, tenant_id, role)
        VALUES ($1, $2, $3, $4, $5);
    """
    await db.execute(
        query_insert,
        schema.name,
        schema.email,
        hash_password(schema.password),
        schema.tenant_id,
        "consultant"
    )

    row = await db.fetchrow(
        "SELECT id, name, email, tenant_id, role FROM users WHERE email = $1",
        schema.email
    )
    return dict(row)

async def login_user(data: dict) -> str:
    schema = LoginSchema(**data)
    db = await get_db()

    row = await db.fetchrow(
        "SELECT id, email, password_hash, tenant_id, role FROM users WHERE email = $1",
        schema.email
    )
    if not row:
        raise ValueError("Credenciais inválidas")

    if not verify_password(schema.password, row["password_hash"]):
        raise ValueError("Credenciais inválidas")

    token = create_access_token(
        sub=row["email"],
        tenant_id=row["tenant_id"],
        role=row["role"]
    )
    return token