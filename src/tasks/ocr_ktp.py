import re
from pathlib import Path
from typing import Dict

import cv2
import numpy as np

# Try importing easyocr, fallback to empty data if not installed properly yet
try:
    import easyocr
    # Initialize reader once to avoid reloading model each time
    # 'id' for Indonesian, 'en' for English
    _reader = easyocr.Reader(['id', 'en'], gpu=False, verbose=False)
except ImportError:
    _reader = None

def extract_ktp_data(image_path: Path) -> Dict[str, str]:
    """Extracts data from a KTP image using EasyOCR for high accuracy."""
    data = {
        "nik": "",
        "nama": "",
        "ttl": "",
        "alamat": ""
    }
    if _reader is None:
        print("EasyOCR not found. Please wait for installation to finish.")
        return data
        
    try:
        # EasyOCR works directly on images
        result = _reader.readtext(str(image_path), detail=0)
        text_lines = [t.upper() for t in result]
        
        # Whole text for fallback regex
        full_text = " ".join(text_lines)
        
        for i, line in enumerate(text_lines):
            # Extract NIK
            if "NIK" in line or "N1K" in line or "N I K" in line:
                digits = re.sub(r'\D', '', line)
                if len(digits) >= 16:
                    data["nik"] = digits[:16]
            
            # Extract Nama
            if ("NAMA" in line or "NAM " in line) and not data["nama"]:
                parts = line.split(':')
                if len(parts) > 1 and len(parts[-1].strip()) > 2:
                    data["nama"] = re.sub(r'[^A-Z\s]', '', parts[-1]).strip()
                elif i + 1 < len(text_lines):
                    data["nama"] = re.sub(r'[^A-Z\s]', '', text_lines[i+1]).strip()
                    
            # Extract TTL
            if ("LAHIR" in line or "TEMPAT" in line or "LALHIR" in line) and not data["ttl"]:
                match = re.search(r'(\d{2})[-/ ]?(\d{2})[-/ ]?(\d{4})', line)
                if match:
                    data["ttl"] = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                elif i + 1 < len(text_lines):
                    match2 = re.search(r'(\d{2})[-/ ]?(\d{2})[-/ ]?(\d{4})', text_lines[i+1])
                    if match2:
                        data["ttl"] = f"{match2.group(1)}-{match2.group(2)}-{match2.group(3)}"
                        
            # Extract Alamat
            if ("ALAMAT" in line or "ALAM " in line) and not data["alamat"]:
                parts = line.split(':')
                if len(parts) > 1 and len(parts[-1].strip()) > 3:
                    addr = re.sub(r'[^\w\s\./-]', '', parts[-1]).strip()
                    if addr not in ["BARU", ""]:
                        data["alamat"] = addr
                elif i + 1 < len(text_lines):
                    addr = re.sub(r'[^\w\s\./-]', '', text_lines[i+1]).strip()
                    if addr not in ["BARU", ""] and len(addr) > 3:
                        data["alamat"] = addr

        # Fallback regex over whole text
        if not data["nik"]:
            match = re.search(r'\b\d{16}\b', full_text)
            if match:
                data["nik"] = match.group(0)

        if not data["ttl"]:
            match = re.search(r'\b(\d{2})[-/ ]?(\d{2})[-/ ]?(\d{4})\b', full_text)
            if match:
                data["ttl"] = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                
        return data
    except Exception as e:
        print(f"OCR Error: {e}")
        return data
