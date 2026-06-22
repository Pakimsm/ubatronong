from __future__ import annotations

import secrets
import string

from src.models.identity import Identity

_FIRST_NAMES = [
    "Budi", "Siti", "Ahmad", "Dewi", "Rizki", "Fitri", "Andi", "Sri",
    "Muhammad", "Nur", "Reza", "Wati", "Hendra", "Yuni", "Dian", "Agus",
    "Linda", "Eko", "Maya", "Bayu", "Rina", "Fajar", "Ayu", "Doni",
    "Sari", "Wahyu", "Indah", "Yoga", "Putri", "Arif", "Hesti", "Dedi",
    "Citra", "Iwan", "Nisa", "Tono", "Lestari", "Yusuf", "Ani", "Rudi",
]

_LAST_NAMES = [
    "Santoso", "Wijaya", "Kusuma", "Pratama", "Susanto", "Wibowo",
    "Setiawan", "Rahayu", "Utama", "Hidayat", "Nugroho", "Purnomo",
    "Saputra", "Hartono", "Gunawan", "Supriadi", "Wahyudi", "Lestari",
    "Handoko", "Budiman", "Kurniawan", "Maulana", "Firmansyah", "Hakim",
]

_ARTIST_NAMES = [
    # Indonesia
    "Raisa", "Isyana", "Tulus", "Hindia", "Pamungkas", "Afgan", "Andmesh",
    "Lyodra", "Mahalini", "Nadin", "Sal Priadi", "Kunto Aji", "Ardhito",
    "Rendy Pandugo", "Ramengvrl", "Weird Genius", "Dipha Barus",
    "Yura Yunita", "Tiara Andini", "Stereowall", "Petra Sihombing",
    # USA
    "SZA", "Giveon", "Russ", "NF", "Quinn XCII", "Chelsea Cutler",
    "Role Model", "TV Girl", "Still Woozy", "Surfaces", "Coin",
    "Alexander 23", "Jeremy Zucker", "Alec Benjamin", "Cautious Clay",
    "Omar Apollo", "Daniel Caesar", "Gnash", "bülow", "Lennon Stella",
    # UK
    "Celeste", "Raye", "Mabel", "Freya Ridings", "Tom Grennan",
    "Rag'n'Bone Man", "Mahalia", "Jorja Smith", "Jacob Banks",
    "Chloe George", "Gracey", "Griff", "Beabadoobee", "Declan McKenna",
    # Germany
    "Lea", "Lotte", "Elif", "Wincent Weiss", "Mark Forster",
    "Johannes Oerding", "Nico Santos", "Joris", "Benni Blanco",
    "Kontra K", "Cro", "Max Giesinger", "LEA", "Lena",
    # France
    "Angèle", "Stromae", "Aya Nakamura", "Zaz", "Willy William",
    "Roméo Elvis", "Pomme", "Lomepal", "Vianney", "Grand Corps Malade",
    "Clara Luciani", "Hoshi", "Terrenoire", "Eddy de Pretto",
    # Singapore
    "Gentle Bones", "Charlie Lim", "Inch Chua", "Linying", "Sezairi",
    "Shye", "Fariz Jabba", "Faris Jabba", "Sonia Lim", "Nathan Hartono",
    # Korea
    "Zion.T", "Dean", "Crush", "Heize", "Bol4", "Epik High",
    "Loco", "pH-1", "Colde", "Sole", "Offonoff", "Dvwn",
    "Leellamarz", "Penomeco", "Hoody", "Yumdda",
    # Japan
    "Kenshi Yonezu", "Aimyon", "Yorushika", "Yoasobi", "Fujii Kaze",
    "Eve", "Vaundy", "Milet", "Aimer", "Hikaru Utada", "Suda Masaki",
    "Ado", "Reol", "Zutomayo", "Omoinotake",
]

_CITIES = [
    "Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Makassar",
    "Palembang", "Tangerang", "Depok", "Bekasi", "Bogor", "Malang",
]

_STREETS = [
    "Jl. Sudirman", "Jl. Gatot Subroto", "Jl. Diponegoro", "Jl. Ahmad Yani",
    "Jl. Raya Bogor", "Jl. Pemuda", "Jl. Veteran", "Jl. Pahlawan",
    "Jl. Merdeka", "Jl. Kebon Jeruk", "Jl. Mangga Besar", "Jl. Kelapa Gading",
]


def _rand_digits(n: int) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(n))


def generate(artist_name: str = "", birth_year: int = 0) -> Identity:
    first = secrets.choice(_FIRST_NAMES)
    last = secrets.choice(_LAST_NAMES)
    legal_name = f"{first} {last}"

    if not artist_name:
        artist_name = secrets.choice(_ARTIST_NAMES)

    day = secrets.choice(range(1, 29))
    month = secrets.choice(range(1, 13))
    year = birth_year if birth_year else secrets.choice(range(1970, 2001))

    phone = "8" + _rand_digits(9)   # e.g. 812345678901

    city = secrets.choice(_CITIES)
    street = secrets.choice(_STREETS)
    num = secrets.choice(range(1, 200))
    address = f"{street} No. {num}, {city}, Indonesia"

    # KTP-style: 16 digits
    id_number = _rand_digits(16)

    return Identity(
        artist_name=artist_name,
        legal_name=legal_name,
        birth_day=day,
        birth_month=month,
        birth_year=year,
        phone=phone,
        address=address,
        id_type="National ID Card",
        id_number=id_number,
    )
