from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Identity:
    artist_name: str
    legal_name: str
    birth_day: int
    birth_month: int
    birth_year: int
    phone: str           # digits only, without +62 prefix
    address: str
    id_type: str         # "National ID Card" | "Passport" | "Driver's license"
    id_number: str
    id_image_path: Optional[Path] = None
