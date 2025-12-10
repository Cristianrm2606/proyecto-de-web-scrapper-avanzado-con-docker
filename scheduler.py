# Este archivo contiene la lógica para programar y gestionar las tareas del scraper.
# Utiliza el scheduler para ejecutar el scraper en intervalos regulares.


from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from main import ScraperManager
from utils.logger import setup_logger
from dotenv import load_dotenv
import os

load_dotenv()
logger = setup_logger('scheduler')

def scheduled_job():
    """Tarea programada que ejecuta el scraping"""
    logger.info(f"Tarea programada ejecutándose: {datetime.now()}")
    
    manager = ScraperManager()
    success = manager.run_scraping()
    
    if success:
        logger.info("Tarea completada exitosamente")
    else:
        logger.error("Tarea completada con errores")

def main():
    """Inicia el scheduler"""
    interval_minutes = int(os.getenv('SCRAPE_INTERVAL', 30))
    
    logger.info("="*60)
    logger.info("INICIANDO SCHEDULER DE SCRAPING")
    logger.info(f"Intervalo: cada {interval_minutes} minutos")
    logger.info("="*60)
    
    scheduler = BlockingScheduler()
    
    # Agregar tarea programada
    scheduler.add_job(
        scheduled_job,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id='scraping_job',
        name='Web Scraping Job',
        replace_existing=True
    )
    
    # Ejecutar inmediatamente al inicio
    logger.info("Ejecutando primera tarea inmediatamente...")
    scheduled_job()
    
    # Iniciar scheduler
    try:
        logger.info("Scheduler iniciado. Presiona Ctrl+C para detener.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler detenido por el usuario")
        scheduler.shutdown()

if __name__ == '__main__':
    main()