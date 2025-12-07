
DROP TABLE IF EXISTS scraped_files CASCADE;
DROP TABLE IF EXISTS scraped_data CASCADE;
DROP TABLE IF EXISTS scraping_events CASCADE;

-- Tabla principal de datos scrapeados
CREATE TABLE scraped_data (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    price DECIMAL(10, 2),
    original_price DECIMAL(10, 2),
    discount_percentage INTEGER,
    quantity INTEGER,
    page_number INTEGER,
    url TEXT,
    image_url TEXT,
    description TEXT,
    category VARCHAR(200),
    scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    data_hash VARCHAR(64) UNIQUE
);

-- Tabla de archivos descargados
CREATE TABLE scraped_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    file_hash VARCHAR(64) UNIQUE,
    download_url TEXT,
    scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabla de eventos/logs de scraping
CREATE TABLE scraping_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_description TEXT,
    affected_records INTEGER DEFAULT 0,
    execution_time DECIMAL(10, 2),
    status VARCHAR(20),
    error_message TEXT,
    event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_scraped_data_hash ON scraped_data(data_hash);
CREATE INDEX idx_scraped_data_active ON scraped_data(is_active);
CREATE INDEX idx_files_hash ON scraped_files(file_hash);
CREATE INDEX idx_events_date ON scraping_events(event_date DESC);

-- Vista para estadísticas rápidas
CREATE VIEW scraping_stats AS
SELECT 
    COUNT(*) FILTER (WHERE is_active = TRUE) as active_products,
    COUNT(*) FILTER (WHERE is_active = FALSE) as inactive_products,
    MAX(last_modified) as last_scraping,
    COUNT(DISTINCT category) as categories_count
FROM scraped_data;