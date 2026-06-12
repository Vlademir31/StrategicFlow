from dataclasses import dataclass

@dataclass
class CommentSchema:
    id_processo: int
    mensagem: str
