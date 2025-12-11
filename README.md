# Proyecto Web Scraper Avanzado

Plataforma completa de **scraping dinámico y estático**, procesamiento de datos, almacenamiento en PostgreSQL, API en JSON y dashboard interactivo.  
Totalmente contenedorizado con **Docker + Docker Compose**.

---

## 📌 Descripción General

Este sistema realiza scraping de:

- **Sitios dinámicos** (MercadoLibre) con **Playwright**
- **Sitios estáticos** usando **Requests + BeautifulSoup**
- Descarga archivos y detecta cambios mediante **hash SHA-256**
- Guarda toda la información en **PostgreSQL**
- Expone JSON a través de una **API Flask**
- Visualiza datos en un **dashboard web**
- Automatiza scraping cada 30 minutos con **APScheduler**

El proyecto está diseñado siguiendo las exigencias del curso UTN **Tecnologías Web III**.

---

## 🛠 Tecnologías Utilizadas

### 🔍 Scraping
- **Playwright (Chromium headless)** — Scraping dinámico real  
- **BeautifulSoup + Requests** — Scraping estático  
- **Hashing SHA-256** — Detección de cambios  

### 🗄 Base de Datos
- **PostgreSQL 16**  
- **SQL Schema + backups automáticos**

### 🌐 API
- **Flask**, **Flask-CORS**  
- Endpoints REST estructurados  

### 💻 Frontend
- HTML5, CSS3, JavaScript  
- Bootstrap 5  
- FullCalendar.js  

### ⚙ Automatización
- **APScheduler**  
- Scheduler cada 30 min  
- Logging estructurado  

### 🐳 Contenedores
- Docker  
- Docker Compose  
- Imagen con Playwright + Chromium preinstalado  

---

## 📂 Estructura del Proyecto

```
proyecto-scraper/
├── scraper/
│   ├── scraper_dynamic.py
│   └── scraper_static.py
│
├── database/
│   ├── db_manager.py
│   └── __init__.py
│
├── api/
│   └── json_api_server.py
│
├── frontend/
│   ├── index.html
│   └── static/
│       ├── styles.css
│       ├── main.js
│       ├── results.js
│       ├── files.js
│       └── calendar.js
│
├── utils/
│   ├── logger.py
│   ├── helpers.py
│   └── json_generator.py
│
├── data/
│   ├── results.json
│   ├── files.json
│   └── events.json
│
├── logs/
│   └── scraper.log
│
├── downloads/
├── docs/
│   └── guia_inicio.md
│
├── Dockerfile
├── docker-compose.yml
├── main.py
├── scheduler.py
├── setup_database.py
├── database_schema.sql
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙ Configuración (Modo Docker)

### 1️⃣ Crear archivo `.env`

```
DB_HOST=db
DB_PORT=5432
DB_NAME=scraper_db
DB_USER=postgres
DB_PASSWORD=postgres

API_HOST=0.0.0.0
API_PORT=5000

SCRAPE_INTERVAL=30
MAX_PAGES=3
SEARCH_TERM=laptop

STATIC_URL=https://file-examples.com/index.php/sample-documents-download/
```

---

### 2️⃣ Ejecutar Docker Compose

```
docker-compose build
docker-compose up
```

Servicios desplegados:

| Servicio | Descripción |
|---------|-------------|
| scraper_dynamic | Scraping de MercadoLibre |
| scraper_static | Descarga de archivos estáticos |
| scraper_scheduler | Tareas automáticas cada 30 minutos |
| scraper_api | API Flask |
| scraper_db | PostgreSQL |

---

### 3️⃣ Acceder a los servicios

| Servicio | URL |
|----------|-----|
| API | http://localhost:5000 |
| Dashboard | frontend/index.html |
| PostgreSQL | localhost:5432 |

---

## ▶ Uso del Proyecto

### Ejecución manual

```
python main.py
```

### Scheduler

```
python scheduler.py
```

### API

```
python api/json_api_server.py
```

---

## 📡 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Estado de la API |
| GET | `/api/products` | Lista de productos |
| GET | `/api/products/<id>` | Producto individual |
| GET | `/api/files` | Archivos descargados |
| GET | `/api/events` | Eventos del sistema |
| GET | `/api/stats` | Estadísticas |
| GET | `/api/categories` | Categorías detectadas |

---

## ⭐ Funcionalidades Principales

- Scraping dinámico con Playwright (Chromium)
- Scraping estático + descarga de archivos
- Comparación con hashing SHA-256
- Base de datos PostgreSQL integrada
- API REST profesional
- Dashboard moderno y modular
- Calendario de eventos con FullCalendar
- Automatización completa Dockerizada
- Logs detallados y gestión robusta de errores

---

## 🧪 Testing

```
python test_api.py
```

---

## 📝 Detección de Cambios

El sistema detecta:

- Nuevos registros → Insertar  
- Registros modificados → Actualizar  
- Archivos modificados → Reemplazar  
- Archivos eliminados → Borrarlos localmente  

---

## 🎨 Diseño Arquitectónico

```
Scraper dinámico / estático
        ↓
Base de Datos PostgreSQL
        ↓
JSON Generator
        ↓
API Flask
        ↓
Dashboard Web
```

---

## 👥 Autores

- **Cristian Rojas**  
- **Sebastián Alpízar**  
- **Raúl Quesada**  

---

## 🎓 Proyecto Académico UTN

Universidad Técnica Nacional (UTN)  
Ingeniería en Tecnologías de la Información  
Curso: **Tecnologías y Sistemas Web III**  
Profesor: **Andrés Joseph Jiménez Leandro**  
Ciclo III-C, 2025  

---

## 📄 Licencia

Proyecto de uso académico — No comercial.
