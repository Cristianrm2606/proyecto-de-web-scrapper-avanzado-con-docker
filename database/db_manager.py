import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'scraper_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            return conn
        except Exception as e:
            self.logger.error(f"Error conectando a la base de datos: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=False):
        """Ejecuta una consulta SQL"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
                return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            self.logger.error(f"Error ejecutando query: {e}")
            raise
    
    def insert_scraped_data(self, data):
        """Inserta datos scrapeados en la base de datos"""
        query = """
        INSERT INTO scraped_data 
        (title, price, original_price, discount_percentage, quantity, 
         page_number, url, image_url, description, category, data_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (data_hash) 
        DO UPDATE SET 
            price = EXCLUDED.price,
            last_modified = CURRENT_TIMESTAMP
        RETURNING id;
        """
        params = (
            data.get('title'),
            data.get('price'),
            data.get('original_price'),
            data.get('discount_percentage'),
            data.get('quantity'),
            data.get('page_number'),
            data.get('url'),
            data.get('image_url'),
            data.get('description'),
            data.get('category'),
            data.get('data_hash')
        )
        return self.execute_query(query, params)
    
    def insert_file(self, file_data):
        """Inserta información de archivo descargado"""
        query = """
        INSERT INTO scraped_files 
        (filename, file_path, file_type, file_size, file_hash, download_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (file_hash) 
        DO UPDATE SET 
            last_modified = CURRENT_TIMESTAMP
        RETURNING id;
        """
        params = (
            file_data.get('filename'),
            file_data.get('file_path'),
            file_data.get('file_type'),
            file_data.get('file_size'),
            file_data.get('file_hash'),
            file_data.get('download_url')
        )
        return self.execute_query(query, params)
    
    def log_event(self, event_type, description, affected_records=0, 
                  execution_time=0, status='success', error_message=None):
        """Registra un evento de scraping"""
        query = """
        INSERT INTO scraping_events 
        (event_type, event_description, affected_records, execution_time, status, error_message)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        params = (event_type, description, affected_records, execution_time, status, error_message)
        return self.execute_query(query, params)
    
    def get_all_data(self):
        """Obtiene todos los datos activos"""
        query = "SELECT * FROM scraped_data WHERE is_active = TRUE ORDER BY scraped_date DESC"
        return self.execute_query(query, fetch=True)
    
    def get_all_files(self):
        """Obtiene todos los archivos activos"""
        query = "SELECT * FROM scraped_files WHERE is_active = TRUE ORDER BY scraped_date DESC"
        return self.execute_query(query, fetch=True)
    
    def get_events(self, limit=50):
        """Obtiene los últimos eventos"""
        query = "SELECT * FROM scraping_events ORDER BY event_date DESC LIMIT %s"
        return self.execute_query(query, (limit,), fetch=True)