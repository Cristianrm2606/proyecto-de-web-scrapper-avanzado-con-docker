from playwright.sync_api import sync_playwright
import hashlib
import time
from utils.logger import setup_logger

logger = setup_logger('scraper_dynamic')

class DynamicScraper:
    def __init__(self, headless=True):
        self.headless = headless

    def calculate_hash(self, data):
        return hashlib.sha256(str(data).encode('utf-8')).hexdigest()

    def scrape_mercadolibre(self, search_term="laptop", max_pages=1):
        all_products = []

        logger.info(f"Iniciando scraping con Playwright para '{search_term}'")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"]
            )

            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept-Language": "es-ES,es;q=0.9",
                    "Referer": "https://www.google.com/"
                }
            )

            base_url = (
                f"https://listado.mercadolibre.com.ar/{search_term}"
                f"#D[A:{search_term}]&origin=UNKNOWN&as.comp_t=SUG&as.comp_v={search_term[:4]}&as.comp_id=SUG"
            )

            for page_n in range(1, max_pages + 1):
                url = base_url if page_n == 1 else f"{base_url}_Desde_{(page_n-1)*50 + 1}"

                logger.info(f"Scrapeando página {page_n}: {url}")

                page.goto(url, timeout=60000, wait_until="networkidle")

                try:
                    page.wait_for_selector("li.ui-search-layout__item", timeout=20000)
                except:
                    logger.warning("No se detectaron productos (timeout).")
                    continue

                # Scroll para cargar todo
                for _ in range(5):
                    page.mouse.wheel(0, 3000)
                    time.sleep(1)

                # Selección real de productos
                items = page.query_selector_all(
                    "li.ui-search-layout__item, div.ui-search-result__wrapper"
                )

                for el in items[:20]:
                    try:
                        title_el = el.query_selector("h2") or el.query_selector("[class*='title']")
                        if not title_el:
                            continue

                        title = title_el.inner_text().strip()

                        price_el = el.query_selector("span.andes-money-amount__fraction")
                        price = None
                        if price_el:
                            price = float(price_el.inner_text().replace(".", "").replace(",", "."))

                        link_el = el.query_selector("a")
                        url_item = link_el.get_attribute("href") if link_el else None

                        img_el = el.query_selector("img")
                        image_url = img_el.get_attribute("src") if img_el else None

                        product_data = {
                            "title": title[:200],
                            "price": price,
                            "original_price": None,
                            "discount_percentage": None,
                            "quantity": 1,
                            "page_number": page_n,
                            "url": url_item,
                            "image_url": image_url,
                            "description": title[:100],
                            "category": search_term
                        }

                        product_data["data_hash"] = self.calculate_hash(
                            f"{title}{price}{url_item}"
                        )

                        all_products.append(product_data)

                    except Exception as e:
                        logger.warning(f"Error procesando producto: {e}")
                        continue

            browser.close()

        logger.info(f"Scraping finalizado. Total productos: {len(all_products)}")
        return all_products
