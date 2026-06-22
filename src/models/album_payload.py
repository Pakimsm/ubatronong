from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class TrackPayload:
    audio_path: Path
    title: str      # defaults to filename stem (stripped of leading number)


@dataclass
class AlbumPayload:
    album_title: str
    artist: str
    genre: str
    release_date: str       # YYYY-MM-DD
    cover_path: Path
    tracks: List[TrackPayload] = field(default_factory=list)
    songwriter: str = ""    # required by SoundOn

    @staticmethod
    def from_folder(
        folder: Path,
        album_title: str,
        artist: str,
        genre: str,
        release_date: str,
        cover_path: Path,
        songwriter: str = "",
    ) -> "AlbumPayload":
        exts = {".mp3", ".wav", ".flac", ".m4a", ".mp4"}
        files = sorted(f for f in folder.iterdir() if f.suffix.lower() in exts)
        tracks = [TrackPayload(audio_path=f, title=_clean_title(f.stem)) for f in files]
        return AlbumPayload(
            album_title=album_title,
            artist=artist,
            genre=genre,
            release_date=release_date,
            cover_path=cover_path,
            tracks=tracks,
            songwriter=songwriter or artist,
        )


def _clean_title(stem: str) -> str:
    """Strip leading track numbers like '01 - ', '01. ', '1 ' from filename stem."""
    import re
    return re.sub(r"^\d+[\s.\-_]+", "", stem).strip()
