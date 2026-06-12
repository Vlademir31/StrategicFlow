from dataclasses import dataclass
from datetime import date

@dataclass
class CompanySchema:
    razao_social: str
    cnpj: str | None = None
    segmento: str | None = None
    porte_empresa: str | None = None
    numero_funcionarios: int | None = 0

@dataclass
class ContactSchema:
    id_empresa: int
    nome: str
    cargo: str | None = None
    email: str | None = None
    telefone_whatsapp: str | None = None

@dataclass
class OpportunitySchema:
    id_empresa: int
    titulo_proposta: str
    valor_projeto: float = 0.0
    fase_pipeline: str = "Diagnóstico"
    motivo_perda: str | None = None
