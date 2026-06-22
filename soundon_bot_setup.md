# SoundOn Automation Bot — Project Setup

## Prerequisites

Pastikan sudah terinstall sebelum mulai:

- Python 3.10+ → https://www.python.org/downloads/
- Google Chrome (versi terbaru)
- Git → https://git-scm.com/

Cek versi Python:
```bash
python --version
```

---

## 1. Buat struktur folder project

```bash
mkdir soundon-bot
cd soundon-bot

mkdir -p src/modules src/core src/gui data/output data/logs config
touch README.md requirements.txt .env .gitignore
```

Struktur folder yang dihasilkan:
```
soundon-bot/
├── src/
│   ├── modules/
│   │   ├── tarik_data.py
│   │   ├── upload_lagu.py
│   │   └── tarik_dana.py
│   ├── core/
│   │   ├── browser.py
│   │   ├── account_manager.py
│   │   ├── scheduler.py
│   │   └── logger.py
│   └── gui/
│       └── app.py
├── data/
│   ├── output/       ← hasil export Excel
│   └── logs/         ← execution logs
├── config/
│   └── accounts.json ← simpan akun (jangan di-commit!)
├── .env
├── .gitignore
└── requirements.txt
```

---

## 2. Buat virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

Pastikan terminal sudah menunjukkan `(venv)` sebelum lanjut.

---

## 3. Install dependencies

Isi `requirements.txt` dengan:
```
selenium==4.18.1
playwright==1.42.0
openpyxl==3.1.2
pandas==2.2.1
PyQt5==5.15.10
python-dotenv==1.0.1
cryptography==42.0.5
requests==2.31.0
beautifulsoup4==4.12.3
webdriver-manager==4.0.1
```

Lalu install semua sekaligus:
```bash
pip install -r requirements.txt
```

Install Playwright browsers (opsional, jika pakai Playwright):
```bash
playwright install chromium
```

---

## 4. Setup ChromeDriver (untuk Selenium)

Pakai `webdriver-manager` supaya otomatis sync dengan versi Chrome:

```python
# src/core/browser.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def create_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1280,800")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver
```

---

## 5. Setup config akun

Buat `config/accounts.json`:
```json
[
  {
    "id": 1,
    "email": "akun1@gmail.com",
    "password": "password_akun1",
    "active": true
  },
  {
    "id": 2,
    "email": "akun2@gmail.com",
    "password": "password_akun2",
    "active": true
  }
]
```

> ⚠️ **Jangan commit file ini ke Git!** Pastikan `config/` ada di `.gitignore`.

Isi `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
config/accounts.json
data/output/
data/logs/
```

---

## 6. Setup logger

```python
# src/core/logger.py
import logging
import os
from datetime import datetime

def setup_logger(module_name: str) -> logging.Logger:
    os.makedirs("data/logs", exist_ok=True)
    log_file = f"data/logs/{module_name}_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    # Handler ke file
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)

    # Handler ke console (tampil di GUI)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    fmt = logging.Formatter("[%(asctime)s] %(levelname)s — %(message)s", "%H:%M:%S")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
```

---

## 7. Template modul (starter)

```python
# src/modules/tarik_data.py
import json
import time
from src.core.browser import create_driver
from src.core.logger import setup_logger

logger = setup_logger("tarik_data")

SOUNDON_URL = "https://dashboard.soundon.fm"

def load_accounts(path="config/accounts.json"):
    with open(path, "r") as f:
        return [a for a in json.load(f) if a.get("active")]

def login(driver, email, password):
    driver.get(f"{SOUNDON_URL}/login")
    time.sleep(2)
    # TODO: isi selector sesuai elemen halaman login SoundOn
    driver.find_element("css selector", "input[type='email']").send_keys(email)
    driver.find_element("css selector", "input[type='password']").send_keys(password)
    driver.find_element("css selector", "button[type='submit']").click()
    time.sleep(3)
    logger.info(f"Login berhasil: {email}")

def scrape_releases(driver):
    driver.get(f"{SOUNDON_URL}/releases")
    time.sleep(2)
    # TODO: implementasi scraping sesuai struktur HTML halaman releases
    releases = []
    logger.info(f"Berhasil ambil {len(releases)} data release")
    return releases

def run():
    accounts = load_accounts()
    all_data = []

    for acc in accounts:
        driver = create_driver(headless=True)
        try:
            login(driver, acc["email"], acc["password"])
            data = scrape_releases(driver)
            all_data.extend(data)
        except Exception as e:
            logger.error(f"Error pada akun {acc['email']}: {e}")
        finally:
            driver.quit()

    return all_data

if __name__ == "__main__":
    run()
```

---

## 8. Jalankan test pertama

```bash
# Aktifkan venv dulu
venv\Scripts\activate   # Windows
# atau
source venv/bin/activate  # Mac/Linux

# Test browser bisa jalan
python -c "from src.core.browser import create_driver; d = create_driver(False); d.get('https://google.com'); print(d.title); d.quit()"

# Jalankan modul tarik data
python -m src.modules.tarik_data
```

---

## 9. Next steps

Setelah setup selesai, lanjut ke:

- [ ] Inspect elemen halaman login SoundOn (F12 di Chrome) → catat selector CSS/XPath
- [ ] Implementasi `scrape_releases()` di `tarik_data.py`
- [ ] Export hasil ke Excel dengan `openpyxl`
- [ ] Implementasi `upload_lagu.py` — form automation + file upload
- [ ] Implementasi `tarik_dana.py` — navigasi + trigger withdrawal
- [ ] Bangun GUI dengan PyQt5
- [ ] Handle CAPTCHA jika muncul (2captcha / manual solving)

---

## Referensi

- Selenium docs: https://www.selenium.dev/documentation/
- Playwright Python: https://playwright.dev/python/
- webdriver-manager: https://github.com/SergeyPirogov/webdriver_manager
- openpyxl: https://openpyxl.readthedocs.io/
