import asyncio
import questionary
from typing import List

from src.interfaces.browser import IBrowser
from src.interfaces.account_repo import IAccountRepository
from src.core.runner import AppRunner
from src.cli.notifier import RichNotifier
from src.cli.prompts import ask_task_choice

from src.tasks.tes_login import TesLoginTask
from src.tasks.tarik_data import TarikDataTask
from src.tasks.tarik_analitik import TarikAnalitikTask
from src.tasks.upload_lagu import UploadLaguTask
from src.tasks.upload_album import UploadAlbumTask
from src.tasks.verifikasi_akun import VerifikasiAkunTask
from src.tasks.tarik_dana import TarikDanaTask

from src.models.upload_payload import UploadPayload
from src.models.identity import Identity
from src.models.account import Account
import os
from pathlib import Path

async def run_cli(browser: IBrowser, account_repo: IAccountRepository):
    notifier = RichNotifier()
    runner = AppRunner(browser, account_repo, notifier)
    
    notifier.console.print("\n[bold magenta]=== SoundOn Bot CLI ===[/]\n")
    
    while True:
        choice = await ask_task_choice()
        
        if choice == "Exit" or not choice:
            break
            
        task = None
        selected_accounts = None
        if choice == "Tampilkan List Akun":
            accounts = account_repo.get_all()
            if not accounts:
                notifier.console.print("[yellow]Belum ada akun terdaftar.[/]")
            else:
                notifier.console.print("\n[bold cyan]=== Daftar Akun ===[/]")
                for a in accounts:
                    active_text = "[green]Aktif[/]" if a.active else "[red]Nonaktif[/]"
                    status_color = "green" if a.status == "Berhasil Login" else "red" if "Gagal" in a.status else "yellow"
                    profile = a.dolphin_profile_id or "-"
                    notifier.console.print(f"ID: {a.id} | Email: {a.email} | Profil Dolphin: {profile} | Status: {active_text} | Info: [{status_color}]{a.status}[/]")
                notifier.console.print("")
        elif choice == "Tambah Akun":
            email = await questionary.text("Email SoundOn:").ask_async()
            password = await questionary.password("Password:").ask_async()
            profile_id = await questionary.text("ID Profil Dolphin Anty (kosongkan jika pakai backend Chromium):").ask_async()
            existing = account_repo.get_all()
            new_id = (max((a.id for a in existing), default=0) + 1)
            new_acc = Account(
                id=new_id, email=email, password=password, active=True,
                status="Baru Ditambahkan",
                dolphin_profile_id=(profile_id.strip() or None) if profile_id else None,
            )
            account_repo.save(new_acc)
            notifier.success(f"Akun {email} berhasil ditambahkan!")
        elif choice == "Hapus Akun":
            accounts = account_repo.get_all()
            if not accounts:
                notifier.console.print("[yellow]Belum ada akun untuk dihapus.[/]")
            else:
                choices = [questionary.Choice(title=a.email, value=a.id) for a in accounts]
                choices.append(questionary.Choice(title="Batal", value=None))
                acc_id = await questionary.select("Pilih akun yang ingin dihapus:", choices=choices).ask_async()
                if acc_id:
                    account_repo.delete(acc_id)
                    notifier.success("Akun berhasil dihapus!")
        elif choice == "Test Login":
            task = TesLoginTask()
        elif choice == "Verifikasi Akun":
            name = await questionary.text("Nama Artis:").ask_async()
            legal = await questionary.text("Nama Sesuai KTP:").ask_async()
            ident = Identity(
                artist_name=name, legal_name=legal, birth_day=1, birth_month=1, birth_year=2000,
                phone="08123456789", address="Jakarta", id_type="National ID", id_number="1234567890123456"
            )
            task = VerifikasiAkunTask(ident)
        elif choice == "Upload Lagu":
            accounts = [a for a in account_repo.get_active() if a.status == "Berhasil Login"]
            if not accounts:
                notifier.console.print("[yellow]Belum ada akun aktif yang berhasil login.[/]")
                continue
                
            acc_choices = [questionary.Choice(title=a.email, value=a.id) for a in accounts]
            selected_accounts = await questionary.checkbox("Pilih akun untuk di-upload (bisa lebih dari satu, spasi untuk memilih):", choices=acc_choices).ask_async()
            
            if not selected_accounts:
                notifier.console.print("[yellow]Tidak ada akun yang dipilih. Dibatalkan.[/]")
                continue

            track_path = await questionary.path("1. Path ke file audio (.wav/.mp3):").ask_async()
            if not track_path:
                notifier.console.print("[red]Path tidak boleh kosong.[/]")
                continue
            track_path = track_path.strip().strip("'").strip('"').strip().replace("\\ ", " ")
            if not os.path.exists(track_path) or not os.path.isfile(track_path):
                notifier.console.print(f"[red]File tidak ditemukan atau bukan file: {track_path}[/]")
                continue

            artist = await questionary.text("2. Nama Artis Utama:").ask_async()
            
            # 3. Judul lagu sesuai nama file
            title = os.path.splitext(os.path.basename(track_path))[0]
            
            # 4. Genre droplist
            genre = await questionary.select(
                "4. Genre:",
                choices=["Pop", "Hip Hop & Rap", "R&B", "Electronic", "Rock", "Country", "Latin", "K-Pop", "Jazz", "Classical", "Folk & Acoustic", "Indie", "Soundtrack", "Other"]
            ).ask_async()
            
            songwriter_name = await questionary.text("7. Nama Asli Penulis Lagu:").ask_async()
            
            payload = UploadPayload(
                track_path=Path(track_path),
                title=title,
                artist=artist,
                genre=genre,
                songwriter_name=songwriter_name
            )
            task = UploadLaguTask(payload)
        elif choice == "Upload Album":
            accounts = [a for a in account_repo.get_active() if a.status == "Berhasil Login"]
            if not accounts:
                notifier.console.print("[yellow]Belum ada akun aktif yang berhasil login.[/]")
                continue
                
            acc_choices = [questionary.Choice(title=a.email, value=a.id) for a in accounts]
            selected_accounts = await questionary.checkbox("Pilih akun untuk di-upload album (spasi untuk memilih):", choices=acc_choices).ask_async()
            
            if not selected_accounts:
                notifier.console.print("[yellow]Tidak ada akun yang dipilih. Dibatalkan.[/]")
                continue

            folder_path = await questionary.path("Path ke folder lagu (akan jadi judul album):").ask_async()
            if not folder_path:
                notifier.console.print("[red]Path folder tidak boleh kosong.[/]")
                continue
            folder_path = folder_path.strip().strip("'").strip('"').strip().replace("\\ ", " ")
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                notifier.console.print(f"[red]Folder tidak ditemukan atau bukan folder: {folder_path}[/]")
                continue

            title = os.path.basename(os.path.normpath(folder_path))
            
            title_lang = await questionary.select("Bahasa Judul:", choices=["Indonesian", "English", "Other"]).ask_async()
            genre = await questionary.select("Genre Utama:", choices=["Pop", "Rock", "Hip Hop", "R&B", "Electronic", "Acoustic", "Jazz", "Classical", "Other"]).ask_async()
            artist = await questionary.text("Artis Utama:").ask_async()
            
            cover_path = await questionary.path("Path ke gambar cover (jpg/png, wajib):").ask_async()
            if not cover_path:
                notifier.console.print("[red]Path cover tidak boleh kosong.[/]")
                continue
            cover_path = cover_path.strip().strip("'").strip('"').strip().replace("\\ ", " ")
            if not os.path.exists(cover_path) or not os.path.isfile(cover_path):
                notifier.console.print(f"[red]File cover tidak ditemukan atau bukan file: {cover_path}[/]")
                continue

            payload = UploadPayload(
                title=title,
                artist=artist,
                genre=genre,
                subgenre="",
                title_language=title_lang,
                track_path=Path(folder_path),
                cover_path=Path(cover_path),
                release_date=""
            )
            task = UploadAlbumTask(payload)
        elif choice == "Tarik Data":
            task = TarikDataTask()
        elif choice == "Tarik Analitik":
            task = TarikAnalitikTask()
        elif choice == "Tarik Dana":
            task = TarikDanaTask()
            
        if task:
            await runner.run(task, account_ids=selected_accounts)
            
    notifier.console.print("[bold yellow]Exiting...[/]")
