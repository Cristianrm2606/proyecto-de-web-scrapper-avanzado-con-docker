import sys
import os

# Agregar el directorio padre al path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from flask import Flask, jsonify, request
from flask_cors import CORS
from database.db_manager import DatabaseManager
from utils.logger import setup_logger
from utils.helpers import load_json, format_price
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

logger = setup_logger('api_server')
db = DatabaseManager()

# Rutas de archivos JSON
DATA_DIR = 'data'
RESULTS_JSON = os.path.join(DATA_DIR, 'results.json')
FILES_JSON = os.path.join(DATA_DIR, 'files.json')
EVENTS_JSON = os.path.join(DATA_DIR, 'events.json')

@app.route('/')
def home():
    """Endpoint principal"""
    return jsonify({
        'message': 'API de Web Scraping',
        'version': '1.0',
        'endpoints': {
            'products': '/api/products',
            'files': '/api/files',
            'events': '/api/events',
            'stats': '/api/stats',
            'health': '/api/health'
        }
    })

@app.route('/api/health')
def health():
    """Verifica el estado de la API"""
    try:
        # Intentar conectar a la base de datos
        conn = db.get_connection()
        conn.close()
        db_status = 'connected'
    except:
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    """Obtiene todos los productos scrapeados"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        category = request.args.get('category', None)
        
        # Obtener datos de la base de datos
        products = db.get_all_data()
        
        # Filtrar por categoría si se especifica
        if category:
            products = [p for p in products if p.get('category') == category]
        
        # Paginación
        start = (page - 1) * limit
        end = start + limit
        paginated_products = products[start:end]
        
        # Convertir datetime a string para JSON
        for product in paginated_products:
            if 'scraped_date' in product and product['scraped_date']:
                product['scraped_date'] = product['scraped_date'].isoformat()
            if 'last_modified' in product and product['last_modified']:
                product['last_modified'] = product['last_modified'].isoformat()
        
        return jsonify({
            'success': True,
            'total': len(products),
            'page': page,
            'limit': limit,
            'data': paginated_products
        })
    
    except Exception as e:
        logger.error(f"Error en /api/products: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtiene un producto específico por ID"""
    try:
        query = "SELECT * FROM scraped_data WHERE id = %s"
        product = db.execute_query(query, (product_id,), fetch=True)
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Convertir datetime a string
        product_data = dict(product[0])
        if 'scraped_date' in product_data and product_data['scraped_date']:
            product_data['scraped_date'] = product_data['scraped_date'].isoformat()
        if 'last_modified' in product_data and product_data['last_modified']:
            product_data['last_modified'] = product_data['last_modified'].isoformat()
        
        return jsonify({
            'success': True,
            'data': product_data
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo producto {product_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    """Obtiene todos los archivos descargados"""
    try:
        files = db.get_all_files()
        
        # Convertir datetime a string
        for file in files:
            if 'scraped_date' in file and file['scraped_date']:
                file['scraped_date'] = file['scraped_date'].isoformat()
            if 'last_modified' in file and file['last_modified']:
                file['last_modified'] = file['last_modified'].isoformat()
        
        return jsonify({
            'success': True,
            'total': len(files),
            'data': files
        })
    
    except Exception as e:
        logger.error(f"Error en /api/files: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """Obtiene los eventos de scraping"""
    try:
        limit = request.args.get('limit', 50, type=int)
        events = db.get_events(limit)
        
        # Convertir datetime a string
        for event in events:
            if 'event_date' in event and event['event_date']:
                event['event_date'] = event['event_date'].isoformat()
        
        return jsonify({
            'success': True,
            'total': len(events),
            'data': events
        })
    
    except Exception as e:
        logger.error(f"Error en /api/events: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas del scraping"""
    try:
        # Estadísticas de productos
        query_products = """
        SELECT 
            COUNT(*) FILTER (WHERE is_active = TRUE) as active_products,
            COUNT(*) FILTER (WHERE is_active = FALSE) as inactive_products,
            COUNT(DISTINCT category) as total_categories,
            AVG(price) as avg_price,
            MAX(last_modified) as last_scraping
        FROM scraped_data
        """
        product_stats = db.execute_query(query_products, fetch=True)[0]
        
        # Estadísticas de archivos
        query_files = """
        SELECT 
            COUNT(*) as total_files,
            SUM(file_size) as total_size,
            COUNT(DISTINCT file_type) as file_types
        FROM scraped_files
        WHERE is_active = TRUE
        """
        file_stats = db.execute_query(query_files, fetch=True)[0]
        
        # Estadísticas de eventos
        query_events = """
        SELECT 
            COUNT(*) as total_events,
            COUNT(*) FILTER (WHERE status = 'success') as successful_events,
            COUNT(*) FILTER (WHERE status = 'error') as failed_events
        FROM scraping_events
        WHERE event_date > NOW() - INTERVAL '24 hours'
        """
        event_stats = db.execute_query(query_events, fetch=True)[0]
        
        # Convertir Decimal y datetime a tipos serializables
        stats = {
            'products': {
                'active': product_stats.get('active_products', 0),
                'inactive': product_stats.get('inactive_products', 0),
                'categories': product_stats.get('total_categories', 0),
                'avg_price': float(product_stats.get('avg_price', 0)) if product_stats.get('avg_price') else 0,
                'last_scraping': product_stats.get('last_scraping').isoformat() if product_stats.get('last_scraping') else None
            },
            'files': {
                'total': file_stats.get('total_files', 0),
                'total_size_mb': round(file_stats.get('total_size', 0) / (1024 * 1024), 2) if file_stats.get('total_size') else 0,
                'types': file_stats.get('file_types', 0)
            },
            'events_24h': {
                'total': event_stats.get('total_events', 0),
                'successful': event_stats.get('successful_events', 0),
                'failed': event_stats.get('failed_events', 0)
            }
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    
    except Exception as e:
        logger.error(f"Error en /api/stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Obtiene todas las categorías disponibles"""
    try:
        query = "SELECT DISTINCT category FROM scraped_data WHERE is_active = TRUE"
        categories = db.execute_query(query, fetch=True)
        
        category_list = [cat['category'] for cat in categories if cat['category']]
        
        return jsonify({
            'success': True,
            'data': category_list
        })
    
    except Exception as e:
        logger.error(f"Error en /api/categories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    logger.info(f"Iniciando API Flask en {host}:{port}")
    app.run(host=host, port=port, debug=True)