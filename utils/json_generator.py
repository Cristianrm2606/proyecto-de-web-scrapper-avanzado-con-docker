import json
import os
from database.db_manager import DatabaseManager
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger('json_generator')
db = DatabaseManager()

class JSONGenerator:
    def __init__(self):
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    def datetime_converter(self, obj):
        """Convierte objetos datetime a string"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    def generate_results_json(self):
        """Genera results.json con todos los productos"""
        try:
            products = db.get_all_data()
            
            # Convertir a lista de diccionarios serializables
            products_list = []
            for product in products:
                product_dict = dict(product)
                # Convertir datetime a string
                for key, value in product_dict.items():
                    if isinstance(value, datetime):
                        product_dict[key] = value.isoformat()
                products_list.append(product_dict)
            
            output_file = os.path.join(self.data_dir, 'results.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(products_list, f, ensure_ascii=False, indent=2)
            
            logger.info(f"results.json generado con {len(products_list)} productos")
            return True
            
        except Exception as e:
            logger.error(f"Error generando results.json: {e}")
            return False
    
    def generate_files_json(self):
        """Genera files.json con todos los archivos descargados"""
        try:
            files = db.get_all_files()
            
            # Convertir a lista de diccionarios serializables
            files_list = []
            for file in files:
                file_dict = dict(file)
                # Convertir datetime a string
                for key, value in file_dict.items():
                    if isinstance(value, datetime):
                        file_dict[key] = value.isoformat()
                files_list.append(file_dict)
            
            output_file = os.path.join(self.data_dir, 'files.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(files_list, f, ensure_ascii=False, indent=2)
            
            logger.info(f"files.json generado con {len(files_list)} archivos")
            return True
            
        except Exception as e:
            logger.error(f"Error generando files.json: {e}")
            return False
    
    def generate_events_json(self):
        """Genera events.json con los eventos de scraping"""
        try:
            events = db.get_events(limit=100)
            
            # Convertir a lista de diccionarios serializables
            events_list = []
            for event in events:
                event_dict = dict(event)
                # Convertir datetime a string
                for key, value in event_dict.items():
                    if isinstance(value, datetime):
                        event_dict[key] = value.isoformat()
                events_list.append(event_dict)
            
            output_file = os.path.join(self.data_dir, 'events.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(events_list, f, ensure_ascii=False, indent=2)
            
            logger.info(f"events.json generado con {len(events_list)} eventos")
            return True
            
        except Exception as e:
            logger.error(f"Error generando events.json: {e}")
            return False
    
    def generate_all_json(self):
        """Genera todos los archivos JSON"""
        logger.info("Generando todos los archivos JSON...")
        
        results = {
            'results.json': self.generate_results_json(),
            'files.json': self.generate_files_json(),
            'events.json': self.generate_events_json()
        }
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"JSON generados: {success_count}/{len(results)} exitosos")
        
        return all(results.values())