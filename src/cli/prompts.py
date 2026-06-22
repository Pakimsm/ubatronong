import questionary

async def ask_task_choice() -> str:
    return await questionary.select(
        "Pilih fitur yang ingin dijalankan:",
        choices=[
            "Tampilkan List Akun",
            "Tambah Akun",
            "Hapus Akun",
            "Test Login",
            "Verifikasi Akun",
            "Upload Lagu",
            "Upload Album",
            "Tarik Data",
            "Tarik Analitik",
            "Tarik Dana",
            "Exit"
        ]
    ).ask_async()
