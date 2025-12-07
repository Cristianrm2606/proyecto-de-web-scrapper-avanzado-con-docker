// Gestión de archivos descargados
let filesData = [];

// Cargar archivos desde la API
async function loadFiles() {
    try {
        showLoading('files-table-body');
        
        const response = await fetch(`${API_BASE_URL}/api/files`);
        const data = await response.json();
        
        if (data.success) {
            filesData = data.data;
            displayFiles(data.data);
        } else {
            showAlert('Error cargando archivos', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('No se pudo conectar con el servidor', 'danger');
    }
}

// Mostrar archivos en la tabla
function displayFiles(files) {
    const tbody = document.getElementById('files-table-body');
    
    if (files.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay archivos descargados</td></tr>';
        return;
    }
    
    tbody.innerHTML = files.map(file => `
        <tr>
            <td>${file.id}</td>
            <td>
                <i class="${getFileIcon(file.file_type)} me-2"></i>
                ${file.filename}
            </td>
            <td><span class="badge bg-info">${getFileTypeLabel(file.file_type)}</span></td>
            <td>${formatFileSize(file.file_size)}</td>
            <td>
                <code style="font-size: 0.75rem;">${truncateHash(file.file_hash)}</code>
                <button class="btn btn-sm btn-outline-secondary ms-1" onclick="copyToClipboard('${file.file_hash}')" title="Copiar hash completo">
                    <i class="bi bi-clipboard"></i>
                </button>
            </td>
            <td>
                <small>${formatDate(file.scraped_date)}</small>
                ${file.last_modified !== file.scraped_date ? `<br><small class="text-warning">Modificado: ${formatDate(file.last_modified)}</small>` : ''}
            </td>
        </tr>
    `).join('');
}

// Obtener icono según tipo de archivo
function getFileIcon(fileType) {
    if (!fileType) return 'bi bi-file-earmark';
    
    const type = fileType.toLowerCase();
    
    if (type.includes('pdf')) return 'bi bi-file-pdf text-danger';
    if (type.includes('image') || type.includes('jpg') || type.includes('png')) return 'bi bi-file-image text-primary';
    if (type.includes('video') || type.includes('mp4')) return 'bi bi-file-play text-info';
    if (type.includes('audio') || type.includes('mp3')) return 'bi bi-file-music text-success';
    if (type.includes('zip') || type.includes('rar')) return 'bi bi-file-zip text-warning';
    if (type.includes('word') || type.includes('doc')) return 'bi bi-file-word text-primary';
    if (type.includes('excel') || type.includes('xls')) return 'bi bi-file-excel text-success';
    
    return 'bi bi-file-earmark';
}

// Obtener etiqueta del tipo de archivo
function getFileTypeLabel(fileType) {
    if (!fileType) return 'Desconocido';
    
    const type = fileType.toLowerCase();
    
    if (type.includes('pdf')) return 'PDF';
    if (type.includes('jpeg') || type.includes('jpg')) return 'JPEG';
    if (type.includes('png')) return 'PNG';
    if (type.includes('mp4')) return 'MP4';
    if (type.includes('mp3')) return 'MP3';
    if (type.includes('zip')) return 'ZIP';
    if (type.includes('doc')) return 'DOC';
    
    return fileType.split('/')[1]?.toUpperCase() || 'Archivo';
}

// Truncar hash para mostrar
function truncateHash(hash) {
    if (!hash) return 'N/A';
    return hash.length > 16 ? hash.substring(0, 16) + '...' : hash;
}

// Copiar al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Hash copiado al portapapeles', 'success');
    }).catch(err => {
        console.error('Error copiando:', err);
        showAlert('Error copiando hash', 'danger');
    });
}

// Filtrar archivos por tipo
function filterFilesByType(type) {
    if (!type || type === 'all') {
        displayFiles(filesData);
        return;
    }
    
    const filtered = filesData.filter(file => 
        file.file_type && file.file_type.toLowerCase().includes(type.toLowerCase())
    );
    
    displayFiles(filtered);
}