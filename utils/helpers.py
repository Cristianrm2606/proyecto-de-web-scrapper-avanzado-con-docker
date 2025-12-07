import hashlib
import json
import os
from datetime import datetime

def calculate_file_hash(filepath):
    """Calcula el hash SHA-256 de un archivo"""
    sha256_hash = hashlib.sha256()
    
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()

def save_json(data, filepath):
    """Guarda datos en formato JSON"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath):
    """Carga datos desde un archivo JSON"""
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_price(price):
    """Formatea un precio a string"""
    if price is None:
        return "N/A"
    return f"${price:,.2f}"

def get_timestamp():
    """Retorna timestamp actual"""
    return datetime.now().isoformat()

def clean_text(text):
    """Limpia texto eliminando espacios extras"""
    if not text:
        return ""
    return " ".join(text.split())

def ensure_dir(directory):
    """Asegura que un directorio exista"""
    os.makedirs(directory, exist_ok=True)