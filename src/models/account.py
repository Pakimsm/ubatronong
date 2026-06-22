from dataclasses import dataclass, field


@dataclass(frozen=True)
class Account:
    id: int
    email: str
    password: str
    active: bool = True
    status: str = "Baru Ditambahkan"

