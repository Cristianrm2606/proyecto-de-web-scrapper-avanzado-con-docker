// Configuración de la API
const API_BASE_URL = 'http://localhost:5000';

// Estado global
const AppState = {
    currentSection: 'dashboard',
    stats: {},
    categories: []
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard iniciado');
    
    // Configurar navegación
    setupNavigation();
    
    // Cargar datos iniciales
    loadInitialData();
    
    // Configurar actualizaciones automáticas cada 5 minutos
    setInterval(loadInitialData, 300000);
});

// Configurar navegación entre secciones
function setupNavigation() {
    const navLinks = document.querySelectorAll('[data-section]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const section = this.getAttribute('data-section');
            showSection(section);
            
            // Actualizar clase active
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Mostrar sección específica
function showSection(sectionName) {
    // Ocultar todas las secciones
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Mostrar sección seleccionada
    const targetSection = document.getElementById(`section-${sectionName}`);
    if (targetSection) {
        targetSection.style.display = 'block';
        AppState.currentSection = sectionName;
        
        // Cargar datos específicos de la sección
        loadSectionData(sectionName);
    }
}

// Cargar datos iniciales
async function loadInitialData() {
    try {
        // Cargar estadísticas
        await loadStats();
        
        // Cargar categorías
        await loadCategories();
        
        // Cargar eventos recientes
        await loadRecentEvents();
        
    } catch (error) {
        console.error('Error cargando datos iniciales:', error);
        showAlert('Error cargando datos del servidor', 'danger');
    }
}

// Cargar estadísticas
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const data = await response.json();
        
        if (data.success) {
            AppState.stats = data.data;
            updateStatsUI(data.data);
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

// Actualizar UI de estadísticas
function updateStatsUI(stats) {
    document.getElementById('stat-products').textContent = stats.products.active || 0;
    document.getElementById('stat-files').textContent = stats.files.total || 0;
    document.getElementById('stat-categories').textContent = stats.products.categories || 0;
    document.getElementById('stat-events').textContent = stats.events_24h.total || 0;
}

// Cargar categorías
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/categories`);
        const data = await response.json();
        
        if (data.success) {
            AppState.categories = data.data;
            updateCategoriesDropdown(data.data);
        }
    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

// Actualizar dropdown de categorías
function updateCategoriesDropdown(categories) {
    const select = document.getElementById('filter-category');
    
    // Limpiar opciones existentes (excepto "Todas")
    while (select.options.length > 1) {
        select.remove(1);
    }
    
    // Agregar categorías
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        select.appendChild(option);
    });
}

// Cargar eventos recientes
async function loadRecentEvents() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/events?limit=5`);
        const data = await response.json();
        
        if (data.success) {
            displayRecentEvents(data.data);
        }
    } catch (error) {
        console.error('Error cargando eventos:', error);
    }
}

// Mostrar eventos recientes
function displayRecentEvents(events) {
    const container = document.getElementById('recent-events');
    
    if (events.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No hay eventos recientes</p>';
        return;
    }
    
    container.innerHTML = events.map(event => `
        <div class="event-item ${event.status}">
            <strong>${event.event_type}</strong>
            <p class="mb-1">${event.event_description || 'Sin descripción'}</p>
            <small>${formatDate(event.event_date)}</small>
        </div>
    `).join('');
}

// Cargar datos específicos de cada sección
function loadSectionData(sectionName) {
    switch(sectionName) {
        case 'products':
            if (typeof loadProducts === 'function') {
                loadProducts();
            }
            break;
        case 'files':
            if (typeof loadFiles === 'function') {
                loadFiles();
            }
            break;
        case 'calendar':
            if (typeof initCalendar === 'function') {
                initCalendar();
            }
            break;
    }
}

// Utilidades
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatPrice(price) {
    if (!price) return 'N/A';
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

function formatFileSize(bytes) {
    if (!bytes) return 'N/A';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.container-fluid').insertBefore(
        alertDiv, 
        document.querySelector('.container-fluid').firstChild
    );
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Mostrar spinner de carga
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="spinner-container">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </div>
        `;
    }
}