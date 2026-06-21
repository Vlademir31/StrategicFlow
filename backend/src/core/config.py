# C:Users\u000BladeOneDriveDocumentosGitHubStrategicFlow\backendsrccoreconfig.py

import os
from dataclasses import dataclass

@dataclass
class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))  # ✅ Porta 8001 (backend original)
    DB_URL: str = os.getenv(
        "DB_URL",
        "postgresql://vlade:31%4085@localhost:5432/strategic_flow"
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key")
    JWT_ALGORITHM: str = "HS256"


settings = Settings()
