from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import hashlib
import re
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
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Script para evitar detección
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 15)
            
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
    
    def scroll_to_load(self, scroll_pause=2, max_scrolls=5):
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
    
    def extract_price_from_text(self, text):
        """Extrae precio de texto, manejando diferentes formatos"""
        if not text:
            return None
        
        # Buscar números con decimales
        price_match = re.search(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', text)
        if price_match:
            price_str = price_match.group(1)
            # Limpiar: quitar puntos de miles, cambiar coma decimal por punto
            price_str = price_str.replace('.', '').replace(',', '.')
            try:
                return float(price_str)
            except:
                return None
        return None
    
    def find_element_safe(self, parent_element, by, value, default=None):
        """Busca elemento de forma segura, retorna default si no lo encuentra"""
        try:
            return parent_element.find_element(by, value)
        except NoSuchElementException:
            return default
    
    def scrape_mercadolibre(self, search_term="laptop", max_pages=1):
        """Scrapea Mercado Libre con selectores robustos"""
        try:
            if not self.driver:
                self.setup_driver()
            
            base_url = f"https://listado.mercadolibre.com.ar/{search_term.replace(' ', '-')}"
            all_products = []
            
            for page in range(1, max_pages + 1):
                url = f"{base_url}_Desde_{(page-1)*50 + 1}" if page > 1 else base_url
                logger.info(f"Scrapeando página {page}: {url}")
                
                self.driver.get(url)
                time.sleep(4)  # Esperar carga inicial
                
                # Hacer scroll para cargar productos
                self.scroll_to_load(scroll_pause=2, max_scrolls=3)
                time.sleep(2)
                
                # Intentar múltiples estrategias para encontrar productos
                product_containers = []
                
                # Estrategia 1: Buscar por clase específica
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item")
                    if containers:
                        product_containers.extend(containers)
                        logger.info(f"Estrategia 1: {len(containers)} productos encontrados")
                except:
                    pass
                
                # Estrategia 2: Buscar por wrapper
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, "div.ui-search-result__wrapper")
                    if containers:
                        product_containers.extend(containers)
                        logger.info(f"Estrategia 2: {len(containers)} productos encontrados")
                except:
                    pass
                
                # Estrategia 3: Buscar por cards
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, "div.andes-card")
                    if containers:
                        product_containers.extend(containers)
                        logger.info(f"Estrategia 3: {len(containers)} productos encontrados")
                except:
                    pass
                
                # Estrategia 4: Buscar cualquier elemento con clase que contenga 'item' o 'result'
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, "[class*='item'], [class*='result'], [class*='card']")
                    # Filtrar por tamaño para evitar elementos muy pequeños
                    containers = [c for c in containers if len(c.get_attribute('innerHTML')) > 500]
                    if containers:
                        product_containers.extend(containers)
                        logger.info(f"Estrategia 4: {len(containers)} productos encontrados")
                except:
                    pass
                
                # Eliminar duplicados
                unique_containers = []
                seen_html = set()
                for container in product_containers:
                    html = container.get_attribute('innerHTML')[:200]  # Primeros 200 chars para identificar
                    if html not in seen_html:
                        seen_html.add(html)
                        unique_containers.append(container)
                
                logger.info(f"Total de contenedores únicos: {len(unique_containers)}")
                
                # Procesar cada producto
                for container in unique_containers[:20]:  # Limitar a 20 por página para prueba
                    try:
                        # Extraer título
                        title = None
                        title_selectors = [
                            (By.CSS_SELECTOR, "h2.ui-search-item__title"),
                            (By.CSS_SELECTOR, ".ui-search-item__title"),
                            (By.CSS_SELECTOR, "h2"),
                            (By.CSS_SELECTOR, ".ui-search-item__title span"),
                            (By.CSS_SELECTOR, "a.ui-search-item__group__element"),
                            (By.CSS_SELECTOR, "[class*='title']")
                        ]
                        
                        for selector_by, selector_value in title_selectors:
                            try:
                                title_elem = container.find_element(selector_by, selector_value)
                                title_text = title_elem.text.strip()
                                if title_text and len(title_text) > 5:
                                    title = title_text
                                    break
                            except:
                                continue
                        
                        if not title:
                            continue  # Si no hay título, saltar
                        
                        # Extraer precio
                        price = None
                        price_selectors = [
                            (By.CSS_SELECTOR, "span.andes-money-amount__fraction"),
                            (By.CSS_SELECTOR, ".ui-search-price__part"),
                            (By.CSS_SELECTOR, ".price-tag-fraction"),
                            (By.CSS_SELECTOR, ".andes-money-amount"),
                            (By.CSS_SELECTOR, "[class*='price']"),
                            (By.CSS_SELECTOR, "span[class*='price']")
                        ]
                        
                        for selector_by, selector_value in price_selectors:
                            try:
                                price_elem = container.find_element(selector_by, selector_value)
                                price_text = price_elem.text.strip()
                                extracted_price = self.extract_price_from_text(price_text)
                                if extracted_price:
                                    price = extracted_price
                                    break
                            except:
                                continue
                        
                        # Extraer URL del producto
                        url = None
                        try:
                            link_elem = container.find_element(By.TAG_NAME, "a")
                            url = link_elem.get_attribute('href')
                        except:
                            # Buscar cualquier enlace dentro del contenedor
                            try:
                                links = container.find_elements(By.TAG_NAME, "a")
                                if links:
                                    url = links[0].get_attribute('href')
                            except:
                                pass
                        
                        # Extraer imagen
                        image_url = None
                        try:
                            img_elem = container.find_element(By.TAG_NAME, "img")
                            image_url = img_elem.get_attribute('src')
                        except:
                            pass
                        
                        product_data = {
                            'title': title[:200],  # Limitar tamaño
                            'price': price,
                            'original_price': None,
                            'discount_percentage': None,
                            'quantity': 1,
                            'page_number': page,
                            'url': url,
                            'image_url': image_url,
                            'description': title[:100],
                            'category': search_term
                        }
                        
                        # Calcular hash único
                        product_data['data_hash'] = self.calculate_hash(f"{title}{price}{url}")
                        
                        all_products.append(product_data)
                        
                        logger.debug(f"Producto extraído: {title[:50]}... - ${price}")
                        
                    except Exception as e:
                        logger.warning(f"Error procesando producto: {e}")
                        continue
                
                logger.info(f"Página {page}: {len(all_products)} productos acumulados")
                
                # Pequeña pausa entre páginas
                if page < max_pages:
                    time.sleep(2)
            
            logger.info(f"Total de productos scrapeados: {len(all_products)}")
            
            # Si no encontramos nada, probar método alternativo
            if len(all_products) == 0:
                logger.info("Probando método alternativo...")
                all_products = self.scrape_mercadolibre_alternative(search_term, max_pages)
            
            return all_products
            
        except Exception as e:
            logger.error(f"Error en scraping de Mercado Libre: {e}")
            return []
        finally:
            self.close_driver()
    
    def scrape_mercadolibre_alternative(self, search_term="laptop", max_pages=1):
        """Método alternativo para scrapear Mercado Libre"""
        try:
            if not self.driver:
                self.setup_driver()
            
            # Usar búsqueda directa
            search_url = f"https://www.mercadolibre.com.ar/{search_term.replace(' ', '-')}"
            logger.info(f"Usando URL alternativa: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(5)
            
            # Tomar screenshot para debug
            self.driver.save_screenshot('debug_page.png')
            logger.info("Screenshot guardado como debug_page.png")
            
            # Extraer datos usando JavaScript
            script = """
            var products = [];
            var items = document.querySelectorAll('li.ui-search-layout__item, div.andes-card, [class*="item"], [class*="result"]');
            
            for (var i = 0; i < Math.min(items.length, 15); i++) {
                var item = items[i];
                var product = {};
                
                // Título
                var titleElem = item.querySelector('h2.ui-search-item__title, h2, [class*="title"]');
                product.title = titleElem ? titleElem.textContent.trim() : '';
                
                // Precio
                var priceElem = item.querySelector('span.andes-money-amount__fraction, [class*="price"]');
                product.price = priceElem ? priceElem.textContent.trim() : '';
                
                // URL
                var linkElem = item.querySelector('a');
                product.url = linkElem ? linkElem.href : '';
                
                // Imagen
                var imgElem = item.querySelector('img');
                product.image = imgElem ? imgElem.src : '';
                
                if (product.title && product.title.length > 5) {
                    products.push(product);
                }
            }
            return products;
            """
            
            products = self.driver.execute_script(script)
            
            all_products = []
            for i, p in enumerate(products):
                try:
                    price = self.extract_price_from_text(p.get('price', ''))
                    
                    product_data = {
                        'title': p.get('title', '')[:200],
                        'price': price,
                        'original_price': None,
                        'discount_percentage': None,
                        'quantity': 1,
                        'page_number': 1,
                        'url': p.get('url', ''),
                        'image_url': p.get('image', ''),
                        'description': p.get('title', '')[:100],
                        'category': search_term,
                        'data_hash': self.calculate_hash(f"{p.get('title', '')}{price}{p.get('url', '')}")
                    }
                    all_products.append(product_data)
                except:
                    continue
            
            logger.info(f"Método alternativo: {len(all_products)} productos encontrados")
            return all_products
            
        except Exception as e:
            logger.error(f"Error en método alternativo: {e}")
            return []
    
    def scrape_aliexpress(self, search_term="electronics", max_pages=1):
        """Scrapea AliExpress - versión simplificada para demostración"""
        try:
            if not self.driver:
                self.setup_driver()
            
            base_url = f"https://www.aliexpress.com/wholesale?SearchText={search_term.replace(' ', '+')}"
            all_products = []
            
            logger.info(f"Scrapeando AliExpress: {base_url}")
            self.driver.get(base_url)
            time.sleep(5)
            
            # Scroll para cargar productos
            self.scroll_to_load(scroll_pause=2, max_scrolls=3)
            
            # Tomar screenshot para debug
            self.driver.save_screenshot('aliexpress_debug.png')
            logger.info("Screenshot de AliExpress guardado")
            
            # Crear datos de ejemplo para demostración
            sample_products = [
                "Smart Watch Android GPS Bluetooth",
                "Wireless Earbuds Bluetooth 5.0",
                "Laptop Gaming 15.6 Inch",
                "Smartphone Android 128GB",
                "Tablet 10 Inch Android 11",
                "Camera Digital 4K Video",
                "Drone Camera with GPS",
                "Headphones Wireless Noise Cancelling",
                "Keyboard Mechanical Gaming",
                "Mouse Wireless Gaming"
            ]
            
            for i, product_name in enumerate(sample_products[:10]):
                product_data = {
                    'title': f"{product_name} - {search_term.capitalize()}",
                    'price': 50.0 + (i * 10),
                    'original_price': 100.0 + (i * 20),
                    'discount_percentage': 50,
                    'quantity': i + 1,
                    'page_number': 1,
                    'url': f"https://www.aliexpress.com/item/{i+1}.html",
                    'image_url': f"https://via.placeholder.com/150?text=Product+{i+1}",
                    'description': f"Descripción del {product_name.lower()} de alta calidad",
                    'category': search_term,
                    'data_hash': self.calculate_hash(f"{product_name}{i}")
                }
                all_products.append(product_data)
            
            logger.info(f"Productos de ejemplo generados: {len(all_products)}")
            return all_products
            
        except Exception as e:
            logger.error(f"Error en scraping de AliExpress: {e}")
            return []
        finally:
            self.close_driver()