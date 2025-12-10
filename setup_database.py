# Este archivo configura la base de datos para almacenar los datos extraídos por el scraper.
# Incluye la creación de las tablas y configuraciones iniciales.


import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def setup_database():
    """Crea la base de datos y ejecuta el schema"""
    
    print("Configurando base de datos PostgreSQL...")
    print("="*60)
    
    # Conectar a postgres (base de datos por defecto)
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database='postgres',
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verificar si la BD existe
        db_name = os.getenv('DB_NAME', 'scraper_db')
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creando base de datos '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✓ Base de datos '{db_name}' creada")
        else:
            print(f"✓ Base de datos '{db_name}' ya existe")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error conectando a PostgreSQL: {e}")
        print("\nVerifica que:")
        print("1. PostgreSQL esté instalado y corriendo")
        print("2. Las credenciales en .env sean correctas")
        return False
    
    # Conectar a la BD del proyecto y ejecutar schema
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'scraper_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = conn.cursor()
        
        # Ejecutar schema
        print("\nEjecutando schema SQL...")
        with open('database_schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        cursor.execute(schema)
        conn.commit()
        
        print("✓ Tablas creadas correctamente")
        
        cursor.close()
        conn.close()
        
        print("="*60)
        print("✓ CONFIGURACIÓN COMPLETADA")
        print("\nPuedes ejecutar:")
        print("  python main.py          - Para scraping manual")
        print("  python scheduler.py     - Para scraping automático")
        print("  python api/json_api_server.py - Para iniciar la API")
        
        return True
        
    except Exception as e:
        print(f"✗ Error ejecutando schema: {e}")
        return False

if __name__ == '__main__':
    setup_database()