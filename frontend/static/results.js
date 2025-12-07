// Gestión de productos
let currentPage = 1;
let totalProducts = 0;
const ITEMS_PER_PAGE = 20;

// Cargar productos desde la API
async function loadProducts(page = 1, category = '', search = '') {
    try {
        showLoading('products-table-body');
        
        let url = `${API_BASE_URL}/api/products?page=${page}&limit=${ITEMS_PER_PAGE}`;
        if (category) url += `&category=${encodeURIComponent(category)}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            currentPage = page;
            totalProducts = data.total;
            displayProducts(data.data, search);
            updatePagination(data.total);
        } else {
            showAlert('Error cargando productos', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('No se pudo conectar con el servidor', 'danger');
    }
}

// Mostrar productos en la tabla
function displayProducts(products, searchTerm = '') {
    const tbody = document.getElementById('products-table-body');
    
    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No hay productos disponibles</td></tr>';
        return;
    }
    
    // Filtrar por búsqueda local si existe
    let filteredProducts = products;
    if (searchTerm) {
        filteredProducts = products.filter(p => 
            p.title.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }
    
    tbody.innerHTML = filteredProducts.map(product => `
        <tr>
            <td>${product.id}</td>
            <td>
                <div class="d-flex align-items-center">
                    ${product.image_url ? `<img src="${product.image_url}" alt="Product" style="width: 50px; height: 50px; object-fit: cover; margin-right: 10px; border-radius: 5px;">` : ''}
                    <span>${truncateText(product.title, 60)}</span>
                </div>
            </td>
            <td>
                <strong>${formatPrice(product.price)}</strong>
                ${product.discount_percentage ? `<span class="badge bg-danger ms-2">-${product.discount_percentage}%</span>` : ''}
            </td>
            <td><span class="badge bg-primary">${product.category || 'Sin categoría'}</span></td>
            <td><small>${formatDate(product.scraped_date)}</small></td>
            <td>
                <button class="btn btn-sm btn-info" onclick="viewProductDetail(${product.id})">
                    <i class="bi bi-eye"></i>
                </button>
                ${product.url ? `<a href="${product.url}" target="_blank" class="btn btn-sm btn-primary ms-1"><i class="bi bi-box-arrow-up-right"></i></a>` : ''}
            </td>
        </tr>
    `).join('');
}

// Actualizar paginación
function updatePagination(total) {
    const totalPages = Math.ceil(total / ITEMS_PER_PAGE);
    const pagination = document.getElementById('products-pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Botón anterior
    html += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadProducts(${currentPage - 1}); return false;">Anterior</a>
        </li>
    `;
    
    // Páginas
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadProducts(${i}); return false;">${i}</a>
            </li>
        `;
    }
    
    // Botón siguiente
    html += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadProducts(${currentPage + 1}); return false;">Siguiente</a>
        </li>
    `;
    
    pagination.innerHTML = html;
}

// Ver detalle de producto
async function viewProductDetail(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/products/${productId}`);
        const data = await response.json();
        
        if (data.success) {
            showProductModal(data.data);
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error cargando detalle del producto', 'danger');
    }
}

// Mostrar modal con detalle del producto
function showProductModal(product) {
    const modalHTML = `
        <div class="modal fade" id="productModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${product.title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-4">
                                ${product.image_url ? `<img src="${product.image_url}" class="img-fluid rounded" alt="Product">` : '<div class="bg-light p-5 text-center rounded">Sin imagen</div>'}
                            </div>
                            <div class="col-md-8">
                                <p><strong>Precio:</strong> ${formatPrice(product.price)}</p>
                                ${product.original_price ? `<p><strong>Precio Original:</strong> ${formatPrice(product.original_price)}</p>` : ''}
                                ${product.discount_percentage ? `<p><strong>Descuento:</strong> <span class="badge bg-danger">${product.discount_percentage}%</span></p>` : ''}
                                <p><strong>Categoría:</strong> ${product.category || 'Sin categoría'}</p>
                                <p><strong>Cantidad:</strong> ${product.quantity || 'N/A'}</p>
                                <p><strong>Página:</strong> ${product.page_number || 'N/A'}</p>
                                <p><strong>Fecha de scraping:</strong> ${formatDate(product.scraped_date)}</p>
                                <p><strong>Última modificación:</strong> ${formatDate(product.last_modified)}</p>
                                ${product.description ? `<p><strong>Descripción:</strong><br>${product.description}</p>` : ''}
                                ${product.url ? `<a href="${product.url}" target="_blank" class="btn btn-primary mt-3"><i class="bi bi-box-arrow-up-right"></i> Ver en sitio original</a>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Eliminar modal anterior si existe
    const existingModal = document.getElementById('productModal');
    if (existingModal) existingModal.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('productModal'));
    modal.show();
}

// Aplicar filtros
document.getElementById('btn-apply-filters')?.addEventListener('click', function() {
    const category = document.getElementById('filter-category').value;
    const search = document.getElementById('filter-search').value;
    loadProducts(1, category, search);
});

// Búsqueda en tiempo real
document.getElementById('filter-search')?.addEventListener('input', function(e) {
    const search = e.target.value;
    if (search.length >= 3 || search.length === 0) {
        const category = document.getElementById('filter-category').value;
        loadProducts(1, category, search);
    }
});

function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}