"""Konstanta lintas-layer yang tidak bergantung pada modul lain.

Diletakkan di sini (bukan di src/tasks) agar layer `pages` tidak perlu meng-import
dari layer `tasks` — menghilangkan ketergantungan melingkar (circular import)."""

BASE_URL = "https://www.soundon.global"
