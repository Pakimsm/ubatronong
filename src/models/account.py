from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Account:
    id: int
    email: str
    password: str
    active: bool = True
    status: str = "Baru Ditambahkan"
    # ID profil Dolphin Anty yang dipakai akun ini (untuk backend DolphinBrowser)
    dolphin_profile_id: Optional[str] = None
