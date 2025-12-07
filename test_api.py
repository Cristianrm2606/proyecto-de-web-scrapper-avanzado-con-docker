import requests
import json
from utils.logger import setup_logger

logger = setup_logger('api_test')

BASE_URL = 'http://localhost:5000'

def test_endpoint(endpoint, description):
    """Prueba un endpoint de la API"""
    try:
        url = f"{BASE_URL}{endpoint}"
        logger.info(f"Testing {description}: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ {description} - OK")
            logger.info(f"  Response: {json.dumps(data, indent=2)[:200]}...")
            return True
        else:
            logger.error(f"✗ {description} - Error {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"✗ {description} - Exception: {e}")
        return False

def main():
    """Ejecuta todas las pruebas de la API"""
    logger.info("=" * 60)
    logger.info("INICIANDO PRUEBAS DE API")
    logger.info("=" * 60)
    
    tests = [
        ('/', 'Home'),
        ('/api/health', 'Health Check'),
        ('/api/products', 'Get All Products'),
        ('/api/products?page=1&limit=10', 'Get Products with Pagination'),
        ('/api/files', 'Get All Files'),
        ('/api/events', 'Get Events'),
        ('/api/stats', 'Get Statistics'),
        ('/api/categories', 'Get Categories'),
    ]
    
    results = []
    for endpoint, description in tests:
        result = test_endpoint(endpoint, description)
        results.append(result)
        print()
    
    # Resumen
    logger.info("=" * 60)
    logger.info("RESUMEN DE PRUEBAS")
    logger.info("=" * 60)
    passed = sum(results)
    total = len(results)
    logger.info(f"Pruebas exitosas: {passed}/{total}")
    logger.info(f"Tasa de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        logger.info("✓ Todas las pruebas pasaron!")
    else:
        logger.warning(f"✗ {total - passed} pruebas fallaron")

if __name__ == '__main__':
    main()