// Frontend Logic for Comparador de Plugins y Temas

// Global state
let currentTab = 'plugins';
let currentFilter = 'todos';
let currentThreshold = 80;
let pluginsData = [];
let themesData = [];
let statusInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeThresholdSlider();
    loadData();
    startStatusPolling();
});

// Tab Management
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
}

function switchTab(tabName) {
    currentTab = tabName;
    currentFilter = 'todos';
    
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.dataset.tab === tabName);
    });
    
    // Update filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === 'todos');
    });
    
    // Clear search
    document.getElementById('search-input').value = '';
    
    // Render data
    renderTable();
}

// Threshold Slider
function initializeThresholdSlider() {
    const slider = document.getElementById('threshold-slider');
    const value = document.getElementById('threshold-value');
    
    slider.addEventListener('input', function() {
        currentThreshold = parseInt(this.value);
        value.textContent = currentThreshold + '%';
    });
    
    slider.addEventListener('change', function() {
        loadData();
    });
}

// Scraper Controls
async function scrapeSite(site, type) {
    const btnId = `btn-${site}-${type}`;
    const btn = document.getElementById(btnId);
    btn.disabled = true;
    
    try {
        const response = await fetch(`/api/scrape/${site}/${type}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            console.log('Scraping started:', data.message);
        } else {
            console.error('Scraping error:', data.message);
            btn.disabled = false;
        }
    } catch (error) {
        console.error('Error starting scraper:', error);
        btn.disabled = false;
    }
}

async function compareAll(type) {
    const btnId = `btn-compare-${type}`;
    const btn = document.getElementById(btnId);
    btn.disabled = true;
    
    try {
        const response = await fetch(`/api/compare/${type}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ threshold: currentThreshold })
        });
        const data = await response.json();
        
        if (response.ok) {
            console.log('Comparison started:', data.message);
        } else {
            console.error('Comparison error:', data.message);
            btn.disabled = false;
        }
    } catch (error) {
        console.error('Error starting comparison:', error);
        btn.disabled = false;
    }
}

// Status Polling
function startStatusPolling() {
    statusInterval = setInterval(updateStatus, 2000);
    updateStatus(); // Initial call
}

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        // Update progress bars
        updateProgressBar('pluginswp-plugins', status.pluginswp_plugins);
        updateProgressBar('pluginswp-themes', status.pluginswp_themes);
        updateProgressBar('weadown-plugins', status.weadown_plugins);
        updateProgressBar('weadown-themes', status.weadown_themes);
        
        // Update buttons
        updateButton('btn-pluginswp-plugins', status.pluginswp_plugins.running);
        updateButton('btn-pluginswp-themes', status.pluginswp_themes.running);
        updateButton('btn-weadown-plugins', status.weadown_plugins.running);
        updateButton('btn-weadown-themes', status.weadown_themes.running);
        updateButton('btn-compare-plugins', status.compare_plugins.running);
        updateButton('btn-compare-themes', status.compare_themes.running);
        
        // Reload data if comparison just finished
        if (!status.compare_plugins.running && status.compare_plugins.progress === 100) {
            loadData();
        }
        if (!status.compare_themes.running && status.compare_themes.progress === 100) {
            loadData();
        }
    } catch (error) {
        console.error('Error fetching status:', error);
    }
}

function updateProgressBar(id, status) {
    const progressBar = document.getElementById(`progress-${id}`);
    const progressFill = progressBar.querySelector('.progress-fill');
    const progressMessage = progressBar.querySelector('.progress-message');
    
    progressFill.style.width = status.progress + '%';
    progressMessage.textContent = status.message;
    
    if (status.running) {
        progressBar.classList.add('active');
    } else if (status.progress === 100) {
        progressBar.classList.add('complete');
    }
}

function updateButton(btnId, isRunning) {
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = isRunning;
        if (isRunning) {
            btn.innerHTML = btn.innerHTML.replace('🔄', '<span class="spinner"></span>');
        }
    }
}

// Data Loading
async function loadData() {
    try {
        // Load plugins
        const pluginsResponse = await fetch(`/api/data/plugins?threshold=${currentThreshold}`);
        const pluginsJson = await pluginsResponse.json();
        pluginsData = pluginsJson.data || [];
        
        // Load themes
        const themesResponse = await fetch(`/api/data/themes?threshold=${currentThreshold}`);
        const themesJson = await themesResponse.json();
        themesData = themesJson.data || [];
        
        // Update stats
        updateStats();
        
        // Render table
        renderTable();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function updateStats() {
    const data = currentTab === 'plugins' ? pluginsData : themesData;
    
    const exact = data.filter(d => d.match_type === 'exact' || d.match_type === 'manual').length;
    const similar = data.filter(d => d.match_type === 'similar').length;
    const none = data.filter(d => d.match_type === 'none').length;
    const blacklisted = data.filter(d => d.blacklisted).length;
    
    document.getElementById(`stat-matches-${currentTab}`).textContent = exact + similar;
    document.getElementById(`stat-outdated-${currentTab}`).textContent = 
        data.filter(d => d.match_type !== 'none' && d.match_version && 
                    compareVersions(d.version, d.match_version) < 0).length;
    document.getElementById(`stat-nomatch-${currentTab}`).textContent = none;
    document.getElementById(`stat-blacklisted-${currentTab}`).textContent = blacklisted;
}

// Table Rendering
function renderTable() {
    const data = currentTab === 'plugins' ? pluginsData : themesData;
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    
    // Filter data
    let filtered = data.filter(item => {
        // Search filter
        if (searchTerm && !item.nombre.toLowerCase().includes(searchTerm)) {
            return false;
        }
        
        // Type filter
        if (currentFilter === 'exactos' && item.match_type !== 'exact' && item.match_type !== 'manual') {
            return false;
        }
        if (currentFilter === 'similares' && item.match_type !== 'similar') {
            return false;
        }
        if (currentFilter === 'sin_match' && item.match_type !== 'none') {
            return false;
        }
        if (currentFilter === 'desactualizados' && !isOutdated(item)) {
            return false;
        }
        
        return true;
    });
    
    const containerId = currentTab === 'plugins' ? 'table-container' : 'table-container-themes';
    const tableContainer = document.getElementById(containerId);
    
    if (filtered.length === 0) {
        tableContainer.innerHTML = `
            <div class="empty-state">
                <h3>📭 No hay datos para mostrar</h3>
                <p>Intenta ajustar los filtros o ejecuta los scrapers primero</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Nombre</th>
                        <th>Versión PW</th>
                        <th>Match</th>
                        <th>Versión WD</th>
                        <th>Similitud</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    filtered.forEach(item => {
        const rowClass = item.blacklisted ? 'blacklisted' : '';
        const matchBadge = getMatchBadge(item);
        const versionBadge = getVersionBadge(item);
        const actions = getActionButtons(item);
        
        html += `
            <tr class="${rowClass}">
                <td><strong>${item.nombre}</strong></td>
                <td>${item.version || '-'}</td>
                <td>${matchBadge}</td>
                <td>${versionBadge}</td>
                <td>${item.similarity ? item.similarity + '%' : '-'}</td>
                <td>${actions}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    tableContainer.innerHTML = html;
}

function getMatchBadge(item) {
    if (item.blacklisted) {
        return '<span class="badge badge-gray">⚫ Blacklisted</span>';
    }
    if (item.match_type === 'exact' || item.match_type === 'manual') {
        return `<span class="badge badge-success">✓ ${item.match_name || 'Match'}</span>`;
    }
    if (item.match_type === 'similar') {
        return `<span class="badge badge-info">~ ${item.match_name || 'Similar'}</span>`;
    }
    return '<span class="badge badge-danger">✗ No match</span>';
}

function getVersionBadge(item) {
    if (!item.match_version || item.match_type === 'none') {
        return '-';
    }
    
    const comparison = compareVersions(item.version, item.match_version);
    if (comparison === 0) {
        return `<span class="badge badge-success">${item.match_version}</span>`;
    } else if (comparison < 0) {
        return `<span class="badge badge-warning">⬆ ${item.match_version}</span>`;
    } else {
        return `<span class="badge badge-info">${item.match_version}</span>`;
    }
}

function getActionButtons(item) {
    if (item.blacklisted) {
        return `
            <div class="action-buttons">
                <button class="action-btn" onclick="removeFromBlacklist('${item.nombre}')">🔓 Restore</button>
            </div>
        `;
    }
    
    let html = '<div class="action-buttons">';
    
    if (item.match_url && isOutdated(item)) {
        html += `<button class="action-btn download" onclick="window.open('${item.match_url}', '_blank')">⬇️ Download</button>`;
    }
    
    html += `<button class="action-btn edit" onclick="openEditModal('${item.nombre}')">✏️ Edit</button>`;
    html += `<button class="action-btn delete" onclick="addToBlacklist('${item.nombre}')">🗑️ Delete</button>`;
    html += '</div>';
    
    return html;
}

function isOutdated(item) {
    if (!item.match_version || !item.version) return false;
    return compareVersions(item.version, item.match_version) < 0;
}

function compareVersions(v1, v2) {
    if (!v1 || !v2) return 0;
    
    const parts1 = v1.split('.').map(p => parseInt(p) || 0);
    const parts2 = v2.split('.').map(p => parseInt(p) || 0);
    
    const maxLen = Math.max(parts1.length, parts2.length);
    for (let i = 0; i < maxLen; i++) {
        const p1 = parts1[i] || 0;
        const p2 = parts2[i] || 0;
        if (p1 < p2) return -1;
        if (p1 > p2) return 1;
    }
    return 0;
}

// Filter Management
function setFilter(filter) {
    currentFilter = filter;
    
    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === filter);
    });
    
    renderTable();
}

function searchItems() {
    renderTable();
}

// Modal Management
function openEditModal(itemName) {
    const modal = document.getElementById('edit-modal');
    const data = currentTab === 'plugins' ? pluginsData : themesData;
    const item = data.find(d => d.nombre === itemName);
    
    if (!item) return;
    
    document.getElementById('edit-item-name').value = item.nombre;
    document.getElementById('edit-weadown-url').value = item.match_url || '';
    document.getElementById('edit-weadown-name').value = item.match_name || '';
    document.getElementById('edit-weadown-version').value = item.match_version || '';
    
    modal.classList.add('active');
}

function closeEditModal() {
    document.getElementById('edit-modal').classList.remove('active');
}

async function saveManualMatch() {
    const itemName = document.getElementById('edit-item-name').value;
    const weadownUrl = document.getElementById('edit-weadown-url').value;
    const weadownName = document.getElementById('edit-weadown-name').value;
    const weadownVersion = document.getElementById('edit-weadown-version').value;
    
    try {
        const response = await fetch('/api/config/manual-match', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: currentTab,
                name: itemName,
                weadown_url: weadownUrl,
                weadown_name: weadownName,
                weadown_version: weadownVersion
            })
        });
        
        if (response.ok) {
            closeEditModal();
            loadData();
        } else {
            alert('Error saving manual match');
        }
    } catch (error) {
        console.error('Error saving manual match:', error);
        alert('Error saving manual match');
    }
}

// Blacklist Management
async function addToBlacklist(itemName) {
    if (!confirm(`¿Añadir "${itemName}" a la blacklist?`)) return;
    
    try {
        const response = await fetch('/api/config/blacklist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: currentTab,
                name: itemName,
                reason: 'User blacklisted'
            })
        });
        
        if (response.ok) {
            loadData();
        } else {
            alert('Error adding to blacklist');
        }
    } catch (error) {
        console.error('Error adding to blacklist:', error);
        alert('Error adding to blacklist');
    }
}

async function removeFromBlacklist(itemName) {
    try {
        const response = await fetch(`/api/config/blacklist/${currentTab}/${encodeURIComponent(itemName)}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadData();
        } else {
            alert('Error removing from blacklist');
        }
    } catch (error) {
        console.error('Error removing from blacklist:', error);
        alert('Error removing from blacklist');
    }
}
