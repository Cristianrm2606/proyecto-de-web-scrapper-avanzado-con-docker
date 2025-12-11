from playwright.sync_api import sync_playwright
import hashlib
import random
from utils.logger import setup_logger

logger = setup_logger("scraper_dynamic")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36"
]

class DynamicScraper:
    def __init__(self, headless=True):
        self.headless = headless

    def calculate_hash(self, text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def scrape_mercadolibre(self, search_term="laptop"):
        items = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--disable-dev-shm-usage", "--no-sandbox"]
            )

            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                locale="es-AR"
            )
            page = context.new_page()

            url = f"https://listado.mercadolibre.com.ar/{search_term}"
            logger.info(f"🌍 Cargando página: {url}")

            page.goto(url, timeout=120000, wait_until="load")
            page.wait_for_timeout(2500)

            # ESTE selector sí existe en tu screenshot
            products = page.query_selector_all("div.ui-search-result__wrapper, li.ui-search-layout__item")
            logger.info(f"✔ Detectados {len(products)} items")

            for p in products:

                # ============= SELECTORES REALES 2025 =============
                # TÍTULO: viene dentro del <a class="poly-component__title">
                title_el = p.query_selector("a.poly-component__title")
                if not title_el:
                    continue

                title = title_el.inner_text().strip()
                url_item = title_el.get_attribute("href")

                # PRECIO: es el mismo selector de siempre
                price_el = p.query_selector("span.andes-money-amount__fraction")
                price = None
                if price_el:
                    raw = price_el.inner_text().replace(".", "")
                    if raw.isdigit():
                        price = float(raw)

                # IMAGEN (src o data-src)
                img_el = p.query_selector("img")
                image = None
                if img_el:
                    image = img_el.get_attribute("data-src") or img_el.get_attribute("src")

                # =================================================

                items.append({
                    "title": title,
                    "price": price,
                    "url": url_item,
                    "image_url": image,
                    "description": title[:120],
                    "category": search_term,
                    "data_hash": self.calculate_hash(title + str(price)),
                })

            browser.close()

        logger.info(f"🎉 TOTAL EXTRAÍDOS: {len(items)}")
        return items
