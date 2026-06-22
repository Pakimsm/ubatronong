import json
from pathlib import Path
from typing import List

from src.interfaces.account_repo import IAccountRepository
from src.models.account import Account


class JsonAccountRepository(IAccountRepository):
    def __init__(self, path: Path) -> None:
        self._path = path

    def _load(self) -> List[dict]:
        if not self._path.exists():
            return []
        with self._path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _dump(self, data: List[dict]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all(self) -> List[Account]:
        return [Account(
            id=item["id"],
            email=item["email"],
            password=item["password"],
            active=item.get("active", True),
            status=item.get("status", "Baru Ditambahkan"),
            dolphin_profile_id=item.get("dolphin_profile_id"),
        ) for item in self._load()]

    def get_active(self) -> List[Account]:
        return [a for a in self.get_all() if a.active]

    def save(self, account: Account) -> None:
        data = self._load()
        idx = next(
            (i for i, a in enumerate(data) if a["id"] == account.id), None
        )
        entry = {
            "id": account.id,
            "email": account.email,
            "password": account.password,
            "active": account.active,
            "status": account.status,
            "dolphin_profile_id": account.dolphin_profile_id,
        }
        if idx is not None:
            data[idx] = entry
        else:
            data.append(entry)
        self._dump(data)

    def delete(self, account_id: int) -> None:
        data = self._load()
        data = [item for item in data if item["id"] != account_id]
        self._dump(data)
