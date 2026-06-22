from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class UploadPayload:
    track_path: Path
    title: str
    artist: str
    genre: str
    songwriter_name: str
    release_date: str = ""
    explicit: bool = False
    subgenre: str = ""
    title_language: str = "Indonesian"
