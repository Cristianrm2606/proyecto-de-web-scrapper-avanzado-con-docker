import requests
from bs4 import BeautifulSoup
import hashlib
import os
import re
import time
from urllib.parse import urljoin
from utils.logger import setup_logger

logger = setup_logger('scraper_static')

FILE_EXTENSIONS = [
    ".pdf", ".jpg", ".jpeg", ".png", ".gif",
    ".mp4", ".mp3", ".zip", ".rar",
    ".doc", ".docx", ".xls", ".xlsx"
]

class StaticScraper:
    def __init__(self, download_dir='downloads'):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0)"
        })

    def calculate_hash(self, content):
        return hashlib.sha256(content).hexdigest()

    def download_file(self, url, suggested_name=None):
        try:
            logger.info(f"Descargando archivo: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Determinar nombre del archivo
            filename = suggested_name or url.split("/")[-1].split("?")[0]
            if not filename:
                filename = f"file_{int(time.time())}"

            filepath = os.path.join(self.download_dir, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            return {
                "filename": filename,
                "file_path": filepath,
                "file_type": response.headers.get("Content-Type", "unknown"),
                "file_size": len(response.content),
                "file_hash": self.calculate_hash(response.content),
                "download_url": url,
            }

        except Exception as e:
            logger.error(f"Error descargando {url}: {e}")
            return None

    def scrape_static_page(self, url):
        try:
            logger.info(f"Scrapeando página estática: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            found_files = []

            # 1. Detectar archivos directos en <a href="">
            for a in soup.find_all("a", href=True):
                href = urljoin(url, a["href"])

                if any(ext in href.lower() for ext in FILE_EXTENSIONS):
                    file = self.download_file(href)
                    if file:
                        found_files.append(file)

            # 2. Detectar botones con data-file o data-url
            for btn in soup.find_all(["button", "a"]):
                data_url = (
                    btn.get("data-file")
                    or btn.get("data-url")
                    or btn.get("data-download")
                )
                if data_url:
                    download_link = urljoin(url, data_url)
                    if any(ext in download_link.lower() for ext in FILE_EXTENSIONS):
                        file = self.download_file(download_link)
                        if file:
                            found_files.append(file)

            # 3. Detectar URLs escondidas dentro de scripts con regex
            script_links = re.findall(r'https?://[^\s"\']+', response.text)
            for link in script_links:
                if any(ext in link.lower() for ext in FILE_EXTENSIONS):
                    file = self.download_file(link)
                    if file:
                        found_files.append(file)

            logger.info(f"Total de archivos descargados: {len(found_files)}")
            return found_files

        except Exception as e:
            logger.error(f"Error scrapeando {url}: {e}")
            return []

    def get_local_files(self):
        local = {}
        for filename in os.listdir(self.download_dir):
            path = os.path.join(self.download_dir, filename)
            with open(path, 'rb') as f:
                data = f.read()
            local[filename] = {
                "path": path,
                "hash": self.calculate_hash(data),
                "size": len(data)
            }
        return local
