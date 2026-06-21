# Exportações do módulo auth
from .models import User
from .schemas import RegisterSchema, LoginSchema
from .service import register_user, login_user, hash_password, verify_password
from .routes import setup_auth_routes

__all__ = [
    "User",
    "RegisterSchema",
    "LoginSchema",
    "register_user",
    "login_user",
    "hash_password",
    "verify_password",
    "setup_auth_routes"
]