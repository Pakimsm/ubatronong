"""Paket task otomasi SoundOn.

Sengaja TIDAK meng-import task apa pun di sini. Eager-import sebelumnya
(`from .upload_lagu import ...`) memicu rantai pages<->tasks dan rawan circular
import. Konsumen meng-import submodul langsung, mis.:
    from src.tasks.tes_login import TesLoginTask
"""
