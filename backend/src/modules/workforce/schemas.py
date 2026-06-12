from dataclasses import dataclass

@dataclass
class ConsultantSchema:
    nome: str
    cargo_senioridade: str
    hard_skills: list[str]
    background_setorial: list[str]
    custo_hora: float
    horas_uteis_mes: int = 160

@dataclass
class AllocationSchema:
    id_consultor: int
    id_projeto: int | None
    status_disponibilidade: str
    porcentagem_dedicacao: int
    horas_faturadas_mes: int
    data_termino_prevista: str | None = None
