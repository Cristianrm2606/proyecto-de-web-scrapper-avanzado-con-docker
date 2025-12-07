// Gestión del calendario con FullCalendar
let calendar = null;

// Inicializar calendario
async function initCalendar() {
    if (calendar) {
        calendar.destroy();
    }
    
    const calendarEl = document.getElementById('calendar');
    
    try {
        const events = await loadCalendarEvents();
        
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,listWeek'
            },
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                list: 'Lista'
            },
            events: events,
            eventClick: function(info) {
                showEventDetail(info.event);
            },
            height: 'auto'
        });
        
        calendar.render();
        
    } catch (error) {
        console.error('Error inicializando calendario:', error);
        showAlert('Error cargando calendario', 'danger');
    }
}

// Cargar eventos para el calendario
async function loadCalendarEvents() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/events`);
        const data = await response.json();
        
        if (!data.success) {
            return [];
        }
        
        // Convertir eventos de scraping a formato FullCalendar
        return data.data.map(event => ({
            id: event.id,
            title: event.event_type,
            start: event.event_date,
            description: event.event_description,
            backgroundColor: getEventColor(event.status),
            borderColor: getEventColor(event.status),
            extendedProps: {
                status: event.status,
                affected_records: event.affected_records,
                execution_time: event.execution_time,
                error_message: event.error_message
            }
        }));
        
    } catch (error) {
        console.error('Error cargando eventos:', error);
        return [];
    }
}

// Color según estado del evento
function getEventColor(status) {
    switch(status) {
        case 'success':
            return '#198754';
        case 'error':
            return '#dc3545';
        case 'warning':
            return '#ffc107';
        default:
            return '#0d6efd';
    }
}

// Mostrar detalle del evento
function showEventDetail(event) {
    const props = event.extendedProps;
    
    const modalHTML = `
        <div class="modal fade" id="eventModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-${props.status === 'success' ? 'success' : props.status === 'error' ? 'danger' : 'primary'} text-white">
                        <h5 class="modal-title">${event.title}</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Fecha:</strong> ${formatDate(event.start)}</p>
                        <p><strong>Estado:</strong> <span class="badge bg-${props.status === 'success' ? 'success' : props.status === 'error' ? 'danger' : 'warning'}">${props.status}</span></p>
                        ${event.extendedProps.description ? `<p><strong>Descripción:</strong> ${event.extendedProps.description}</p>` : ''}
                        ${props.affected_records ? `<p><strong>Registros afectados:</strong> ${props.affected_records}</p>` : ''}
                        ${props.execution_time ? `<p><strong>Tiempo de ejecución:</strong> ${props.execution_time}s</p>` : ''}
                        ${props.error_message ? `<div class="alert alert-danger mt-3"><strong>Error:</strong><br>${props.error_message}</div>` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const existingModal = document.getElementById('eventModal');
    if (existingModal) existingModal.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    modal.show();
}

// Agregar evento de scraping al calendario
async function addScrapingEvent(eventData) {
    if (!calendar) return;
    
    calendar.addEvent({
        title: eventData.type,
        start: new Date(),
        backgroundColor: getEventColor(eventData.status),
        borderColor: getEventColor(eventData.status),
        extendedProps: eventData
    });
}