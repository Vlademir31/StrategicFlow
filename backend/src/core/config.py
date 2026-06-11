import os
from dataclasses import dataclass

@dataclass
class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    DB_URL: str = os.getenv(
        "DB_URL",
        "postgresql://strategicflow:strategicflow@db:5432/strategicflow"
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key")
    JWT_ALGORITHM: str = "HS256"


settings = Settings()
