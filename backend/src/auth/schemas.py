from dataclasses import dataclass

@dataclass
class RegisterSchema:
    name: str
    email: str
    password: str
    tenant_id: str = "default-tenant"


@dataclass
class LoginSchema:
    email: str
    password: str