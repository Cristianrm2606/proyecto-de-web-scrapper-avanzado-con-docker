import logging
import json
from datetime import datetime
import os

def setup_logger(name, log_file='logs/scraper.log', level=logging.INFO):
    """Configura el sistema de logging"""
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_json(logger, data, message=""):
    """Registra datos en formato JSON"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'data': data
    }
    logger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))