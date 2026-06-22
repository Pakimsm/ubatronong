from dataclasses import dataclass


@dataclass(frozen=True)
class Release:
    title: str
    videos: int = 0
    views: int = 0
    streams: int = 0
    listeners: int = 0
    engagement: float = 0.0
