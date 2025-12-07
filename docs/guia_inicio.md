notepad docs\guia_inicio.md
```

**Copia y pega esto:**
```
# Guía de Inicio Rápido

## Instalación

### 1. Clonar y Preparar

git clone https://github.com/Cristianrm2606/proyecto-de-web-scrapper-avanzado-con-docker.git
cd proyecto-de-web-scrapper-avanzado-con-docker

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

### 2. Configurar PostgreSQL

Abrir pgAdmin y crear base de datos scraper_db

### 3. Configurar .env

DB_HOST=localhost
DB_PORT=5433
DB_NAME=scraper_db
DB_USER=postgres
DB_PASSWORD=tu_password

API_PORT=5000
SCRAPE_INTERVAL=30

### 4. Inicializar Base de Datos

python setup_database.py

## Ejecutar el Proyecto

Scraping manual:
python main.py

Iniciar API:
python api/json_api_server.py

Iniciar scheduler:
python scheduler.py

Abrir dashboard:
Doble click en frontend/index.html

## Verificar Funcionamiento

API: http://localhost:5000
Productos: http://localhost:5000/api/products
Estadísticas: http://localhost:5000/api/stats

## Problemas Comunes

PostgreSQL no conecta:
Verificar que esté corriendo en services.msc

Puerto ocupado:
Cambiar API_PORT en .env

Módulos no encontrados:
pip install -r requirements.txt

## Personalizar

Cambiar búsqueda en main.py:
search_term='celulares'
max_pages=5

Cambiar intervalo en .env:
SCRAPE_INTERVAL=60

## Estructura Simple

scraper/ - Extracción de datos
database/ - Conexión a PostgreSQL
api/ - Endpoints REST
frontend/ - Dashboard visual
utils/ - Utilidades y logs
main.py - Ejecutor principal
scheduler.py - Automatización

## Comandos Útiles

Ver logs:
Get-Content logs/scraper.log -Wait

Probar API:
python test_api.py

Limpiar BD:
python setup_database.py