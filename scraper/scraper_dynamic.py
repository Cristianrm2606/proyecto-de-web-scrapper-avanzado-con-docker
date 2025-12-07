from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import hashlib
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger('scraper_dynamic')

class DynamicScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.wait = None
    
    def setup_driver(self):
        """Configura el driver de Selenium"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info("Driver de Selenium configurado exitosamente")
        except Exception as e:
            logger.error(f"Error configurando driver: {e}")
            raise
    
    def close_driver(self):
        """Cierra el driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver cerrado")
    
    def calculate_hash(self, data):
        """Calcula hash SHA-256 de los datos"""
        data_str = str(data).encode('utf-8')
        return hashlib.sha256(data_str).hexdigest()
    
    def scroll_to_load(self, scroll_pause=2, max_scrolls=10):
        """Hace scroll para cargar contenido dinámico"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        
        while scrolls < max_scrolls:
            # Scroll hacia abajo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            
            # Calcular nueva altura
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            last_height = new_height
            scrolls += 1
        
        logger.info(f"Scroll completado: {scrolls} scrolls realizados")
    
    def scrape_mercadolibre(self, search_term="laptop", max_pages=3):
        """Ejemplo: Scrapea Mercado Libre"""
        try:
            if not self.driver:
                self.setup_driver()
            
            base_url = f"https://listado.mercadolibre.com.ar/{search_term.replace(' ', '-')}"
            all_products = []
            
            for page in range(1, max_pages + 1):
                url = f"{base_url}_Desde_{(page-1)*50 + 1}" if page > 1 else base_url
                logger.info(f"Scrapeando página {page}: {url}")
                
                self.driver.get(url)
                time.sleep(3)
                
                # Esperar a que carguen los productos
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ui-search-layout__item")))
                
                # Extraer productos
                products = self.driver.find_elements(By.CLASS_NAME, "ui-search-layout__item")
                
                for product in products:
                    try:
                        title = product.find_element(By.CLASS_NAME, "ui-search-item__title").text
                        
                        # Precio
                        try:
                            price_elem = product.find_element(By.CLASS_NAME, "andes-money-amount__fraction")
                            price = float(price_elem.text.replace('.', '').replace(',', '.'))
                        except:
                            price = None
                        
                        # URL
                        try:
                            url_elem = product.find_element(By.TAG_NAME, "a")
                            product_url = url_elem.get_attribute('href')
                        except:
                            product_url = None
                        
                        # Imagen
                        try:
                            img_elem = product.find_element(By.TAG_NAME, "img")
                            image_url = img_elem.get_attribute('src')
                        except:
                            image_url = None
                        
                        product_data = {
                            'title': title,
                            'price': price,
                            'original_price': None,
                            'discount_percentage': None,
                            'quantity': 1,
                            'page_number': page,
                            'url': product_url,
                            'image_url': image_url,
                            'description': title,
                            'category': search_term
                        }
                        
                        # Calcular hash único
                        product_data['data_hash'] = self.calculate_hash(f"{title}{price}{product_url}")
                        
                        all_products.append(product_data)
                        
                    except Exception as e:
                        logger.warning(f"Error extrayendo producto: {e}")
                        continue
                
                logger.info(f"Página {page}: {len(products)} productos encontrados")
            
            logger.info(f"Total de productos scrapeados: {len(all_products)}")
            return all_products
            
        except Exception as e:
            logger.error(f"Error en scraping dinámico: {e}")
            return []
        finally:
            self.close_driver()
    
    def scrape_aliexpress(self, search_term="electronics", max_pages=2):
        """Ejemplo: Scrapea AliExpress"""
        try:
            if not self.driver:
                self.setup_driver()
            
            base_url = f"https://www.aliexpress.com/wholesale?SearchText={search_term.replace(' ', '+')}"
            all_products = []
            
            logger.info(f"Scrapeando AliExpress: {base_url}")
            self.driver.get(base_url)
            time.sleep(5)
            
            # Scroll para cargar productos
            self.scroll_to_load(scroll_pause=2, max_scrolls=5)
            
            # Extraer productos (selectores pueden cambiar)
            products = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='product']")[:30]
            
            for idx, product in enumerate(products):
                try:
                    # Aquí debes adaptar los selectores según la estructura actual de AliExpress
                    title = product.find_element(By.CSS_SELECTOR, "h1, h2, h3, [class*='title']").text
                    
                    product_data = {
                        'title': title,
                        'price': None,
                        'original_price': None,
                        'discount_percentage': None,
                        'quantity': 1,
                        'page_number': 1,
                        'url': None,
                        'image_url': None,
                        'description': title,
                        'category': search_term,
                        'data_hash': self.calculate_hash(f"{title}{idx}")
                    }
                    
                    all_products.append(product_data)
                    
                except Exception as e:
                    continue
            
            logger.info(f"Total de productos scrapeados: {len(all_products)}")
            return all_products
            
        except Exception as e:
            logger.error(f"Error en scraping de AliExpress: {e}")
            return []
        finally:
            self.close_driver()