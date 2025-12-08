
# Proyecto Web Scraper Avanzado

Plataforma de scraping y visualización de datos con automatización, base de datos PostgreSQL y dashboard interactivo.

## Descripción

Sistema completo de web scraping que extrae datos de sitios dinámicos (Mercado Libre) y estáticos, almacena la información en PostgreSQL, expone APIs REST en JSON y visualiza todo en un dashboard moderno.

## Tecnologías

- Backend: Python 3.9+
- Web Scraping: Selenium, BeautifulSoup, Requests
- Base de Datos: PostgreSQL 16
- API: Flask + Flask-CORS
- Frontend: HTML5, CSS3, JavaScript, Bootstrap 5
- Calendario: FullCalendar.js
- Automatización: APScheduler

## Estructura del Proyecto
```bash
proyecto-scraper/
├── scraper/
│   ├── scraper_dynamic.py
│   └── scraper_static.py
├── database/
│   ├── db_manager.py
│   └── __init__.py
├── api/
│   └── json_api_server.py
├── frontend/
│   ├── index.html
│   └── static/
│       ├── styles.css
│       ├── main.js
│       ├── results.js
│       ├── files.js
│       └── calendar.js
├── utils/
│   ├── logger.py
│   ├── helpers.py
│   └── json_generator.py
├── data/
│   ├── results.json
│   ├── files.json
│   └── events.json
├── logs/
│   └── scraper.log
├── downloads/
├── docs/
│   └── guia_inicio.md
├── main.py
├── scheduler.py
├── setup_database.py
├── database_schema.sql
├── requirements.txt
├── .env
└── README.md
```
## Configuración

### 1. Instalar PostgreSQL

Descargar e instalar PostgreSQL 16 desde postgresql.org
Crear base de datos scraper_db
Anotar la contraseña del usuario postgres

### 2. Clonar el Repositorio

git clone https://github.com/Cristianrm2606/proyecto-de-web-scrapper-avanzado-con-docker.git
cd proyecto-de-web-scrapper-avanzado-con-docker

### 3. Crear Entorno Virtual

python -m venv venv
venv\Scripts\activate

### 4. Instalar Dependencias

pip install -r requirements.txt

### 5. Configurar Variables de Entorno

Editar el archivo .env con tus credenciales:

DB_HOST=localhost
DB_PORT=5433
DB_NAME=scraper_db
DB_USER=postgres
DB_PASSWORD=tu_password_aqui

API_HOST=0.0.0.0
API_PORT=5000

SCRAPE_INTERVAL=30
MAX_PAGES=3
SEARCH_TERM=laptop
STATIC_URL=https://file-examples.com/

OPENAI_API_KEY=tu_api_key

### 6. Inicializar Base de Datos

python setup_database.py

## Uso

### Ejecutar Scraping Manual

python main.py

### Iniciar Scheduler (Automático cada 30 min)

python scheduler.py

### Iniciar API

python api/json_api_server.py

La API estará disponible en: http://localhost:5000

### Abrir Dashboard

1. Iniciar la API
2. Abrir frontend/index.html en el navegador
3. O usar Live Server en VS Code

## Endpoints de la API

GET / - Información de la API
GET /api/health - Estado del servidor
GET /api/products - Lista de productos
GET /api/products/<id> - Detalle de producto
GET /api/files - Archivos descargados
GET /api/events - Eventos de scraping
GET /api/stats - Estadísticas generales
GET /api/categories - Categorías disponibles

## Funcionalidades

- Scraping de sitios dinámicos (Mercado Libre, AliExpress)
- Scraping de sitios estáticos con descarga de archivos
- Detección de cambios con hash SHA-256
- Base de datos PostgreSQL con schema completo
- API REST con paginación y filtros
- Dashboard interactivo con estadísticas
- Calendario de eventos con FullCalendar
- Automatización con APScheduler
- Sistema de logs estructurado
- Manejo robusto de errores

## Testing

Probar la API:

python test_api.py

## Logs

Los logs se guardan en logs/scraper.log con formato estructurado JSON.

## Detección de Cambios

El sistema detecta automáticamente:
- Nuevos registros: Inserta + Alerta
- Registros modificados: Actualiza + Alerta
- Archivos modificados (hash diferente): Reemplaza
- Archivos eliminados: Elimina localmente

## Diseño del Sistema

El proyecto sigue una arquitectura modular con separación de responsabilidades:

1. Capa de Scraping: scraper_dynamic.py y scraper_static.py manejan la extracción de datos
2. Capa de Datos: database/db_manager.py gestiona todas las operaciones con PostgreSQL
3. Capa de API: json_api_server.py expone los datos mediante endpoints REST
4. Capa de Presentación: frontend/ contiene el dashboard interactivo
5. Capa de Automatización: scheduler.py ejecuta tareas programadas
6. Utilidades: utils/ contiene helpers, logging y generación de JSON

Flujo de Datos:
Scraping -> Base de Datos -> JSON Files -> API -> Dashboard

## Autor

Cristian Rojas 
Sebastian Alpizar
Raul Quesada


## Proyecto Académico

Universidad Técnica Nacional (UTN)
Ingeniería en Tecnologías de la Información
Ciclo: IIIC-2025
Profesor: Andrés Joseph Jiménez Leandro

## Notas Importantes

- El scraper respeta las políticas de robots.txt de los sitios
- Los datos son para uso educativo únicamente
- Se recomienda no ejecutar el scraper con intervalos menores a 30 minutos
- Mantener actualizado el requirements.txt con las versiones correctas

## Licencia

Este proyecto es de uso académico.