import time
from datetime import datetime
from scraper.scraper_dynamic import DynamicScraper
from scraper.scraper_static import StaticScraper
from database.db_manager import DatabaseManager
from utils.logger import setup_logger
from utils.json_generator import JSONGenerator
from dotenv import load_dotenv
import os

load_dotenv()
logger = setup_logger('main')

class ScraperManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.json_gen = JSONGenerator()
        self.dynamic_scraper = DynamicScraper(headless=True)
        self.static_scraper = StaticScraper()
        
    def run_scraping(self):
        logger.info("="*60)
        logger.info("INICIANDO PROCESO DE SCRAPING")
        logger.info("="*60)
        
        start_time = time.time()
        total_new = 0
        total_updated = 0
        
        try:
            # Scraping dinámico
            logger.info("Ejecutando scraping dinámico...")
            search_term = os.getenv('SEARCH_TERM', 'laptop')

            # 🔥 FIX: eliminar max_pages
            products = self.dynamic_scraper.scrape_mercadolibre(
                search_term=search_term
            )
            
            logger.info(f"Productos obtenidos: {len(products)}")
            
            # Guardar en base de datos
            for product in products:
                try:
                    result = self.db.insert_scraped_data(product)
                    if result:
                        total_new += 1
                except Exception as e:
                    logger.warning(f"Error insertando producto: {e}")
                    total_updated += 1
            
            logger.info(f"Nuevos: {total_new}, Actualizados: {total_updated}")
            
            # Scraping estático
            logger.info("Ejecutando scraping estático...")
            static_url = os.getenv('STATIC_URL', 'https://file-examples.com/index.php/sample-documents-download/')
            
            files = self.static_scraper.scrape_static_page(static_url)
            
            for file in files:
                try:
                    self.db.insert_file(file)
                except Exception as e:
                    logger.warning(f"Error insertando archivo: {e}")
            
            logger.info(f"Archivos descargados: {len(files)}")
            
            # Generar JSONs
            logger.info("Generando archivos JSON...")
            self.json_gen.generate_all_json()
            
            execution_time = round(time.time() - start_time, 2)
            self.db.log_event(
                event_type='scraping_completed',
                description=f'Scraping completado exitosamente. Nuevos: {total_new}, Actualizados: {total_updated}',
                affected_records=total_new + total_updated,
                execution_time=execution_time,
                status='success'
            )
            
            logger.info(f"Proceso completado en {execution_time}s")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error en proceso de scraping: {e}")
            
            execution_time = round(time.time() - start_time, 2)
            self.db.log_event(
                event_type='scraping_error',
                description='Error en proceso de scraping',
                execution_time=execution_time,
                status='error',
                error_message=str(e)
            )
            
            return False
    
    def setup_database(self):
        logger.info("Configurando base de datos...")
        
        try:
            with open('database_schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(schema)
            conn.commit()
            conn.close()
            
            logger.info("Base de datos configurada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error configurando base de datos: {e}")
            return False

def main():
    manager = ScraperManager()
    
    setup_db = os.getenv('SETUP_DATABASE', 'false').lower() == 'true'
    
    if setup_db:
        logger.info("Modo setup: Inicializando base de datos...")
        manager.setup_database()
    
    success = manager.run_scraping()
    
    if success:
        logger.info("✓ Proceso finalizado exitosamente")
    else:
        logger.error("✗ Proceso finalizado con errores")

if __name__ == '__main__':
    main()
