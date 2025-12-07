import requests
from bs4 import BeautifulSoup
import hashlib
import os
from datetime import datetime
from utils.logger import setup_logger
import time

logger = setup_logger('scraper_static')

class StaticScraper:
    def __init__(self, download_dir='downloads'):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def calculate_hash(self, content):
        """Calcula el hash SHA-256 del contenido"""
        return hashlib.sha256(content).hexdigest()
    
    def download_file(self, url, filename=None):
        """Descarga un archivo y retorna su información"""
        try:
            logger.info(f"Descargando archivo: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Obtener nombre del archivo
            if not filename:
                filename = url.split('/')[-1].split('?')[0]
                if not filename:
                    filename = f"file_{int(time.time())}"
            
            # Calcular hash
            file_hash = self.calculate_hash(response.content)
            
            # Guardar archivo
            file_path = os.path.join(self.download_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            file_info = {
                'filename': filename,
                'file_path': file_path,
                'file_type': response.headers.get('Content-Type', 'unknown'),
                'file_size': len(response.content),
                'file_hash': file_hash,
                'download_url': url
            }
            
            logger.info(f"Archivo descargado exitosamente: {filename}")
            return file_info
            
        except Exception as e:
            logger.error(f"Error descargando archivo {url}: {e}")
            return None
    
    def scrape_static_page(self, url):
        """Scrapea una página estática HTML"""
        try:
            logger.info(f"Scrapeando página estática: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar todos los enlaces de descarga
            files = []
            
            # Links con extensiones comunes
            download_links = soup.find_all('a', href=True)
            
            for link in download_links:
                href = link.get('href')
                
                # Filtrar por extensiones de archivo
                if any(ext in href.lower() for ext in ['.pdf', '.jpg', '.png', '.mp4', '.mp3', '.zip', '.doc', '.docx']):
                    # Construir URL completa si es relativa
                    if not href.startswith('http'):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    
                    file_info = self.download_file(href)
                    if file_info:
                        files.append(file_info)
            
            logger.info(f"Total de archivos descargados: {len(files)}")
            return files
            
        except Exception as e:
            logger.error(f"Error scrapeando página estática {url}: {e}")
            return []
    
    def check_file_changes(self, existing_hash, new_hash):
        """Verifica si un archivo ha cambiado"""
        return existing_hash != new_hash
    
    def get_local_files(self):
        """Obtiene lista de archivos locales con sus hashes"""
        local_files = {}
        
        if not os.path.exists(self.download_dir):
            return local_files
        
        for filename in os.listdir(self.download_dir):
            file_path = os.path.join(self.download_dir, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                    file_hash = self.calculate_hash(content)
                    local_files[filename] = {
                        'path': file_path,
                        'hash': file_hash,
                        'size': len(content)
                    }
        
        return local_files