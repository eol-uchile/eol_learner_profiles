export function formatTime(minutes) {
    if (!minutes) return '0 min';
    minutes = Math.round(minutes);
    var hours = Math.floor(minutes / 60);
    var remainingMinutes = minutes % 60;
    if (hours > 0) return remainingMinutes === 0 ? hours + 'h' : hours + 'h ' + remainingMinutes + 'min';
    return minutes + ' min';
}

export function getXLabel(d, view) {
    if (view === 'week') return d.date_label || ('Semana ' + d.week);
    var match = d.name.match(/^Módulo (\d+)/i);
    return match ? ('Mód. ' + match[1]) : d.name;
}

// --- Tooltips ---
let globalTooltipEl = null;

function getTooltip() {
    if (!globalTooltipEl) {
        globalTooltipEl = document.createElement('div');
        globalTooltipEl.className = 'd3-tooltip';
        document.body.appendChild(globalTooltipEl);
    }
    return globalTooltipEl;
}

export function showTooltip(e, html) {
    var t = getTooltip();
    t.innerHTML = html;
    t.style.opacity = 1;
    moveTooltip(e);
}

export function moveTooltip(e) {
    var pageX = e.pageX || (e.touches && e.touches[0].pageX) || 0;
    var pageY = e.pageY || (e.touches && e.touches[0].pageY) || 0;
    var t = getTooltip();
    t.style.left = (pageX > window.innerWidth - 150 ? pageX - 120 : pageX + 15) + 'px';
    t.style.top = (pageY - 30) + 'px';
}

export function hideTooltip() { 
    if(globalTooltipEl) globalTooltipEl.style.opacity = 0; 
}

// --- Recs y colapsables ---
export function applyRecommendationCollapse(contentId, btnId) {
    var content = document.getElementById(contentId);
    var btn = document.getElementById(btnId);
    if (!content || !btn) return;
    var text = content.textContent.trim();
    
    if (text.length > 90 && text !== 'Cargando recomendación...') {
        content.classList.add('collapsed');
        content.style.maxHeight = '26px';
        btn.style.display = 'inline-block';
        btn.textContent = 'Ver más';
    } else {
        content.classList.remove('collapsed');
        content.style.maxHeight = 'none';
        btn.style.display = 'none';
    }
}

export function toggleRec(contentId, btnId) {
    var content = document.getElementById(contentId);
    var btn = document.getElementById(btnId);
    if (!content || !btn) return;
    var isCollapsed = content.classList.contains('collapsed');
    content.classList.toggle('collapsed');
    content.style.maxHeight = isCollapsed ? content.scrollHeight + 'px' : '26px';
    btn.textContent = isCollapsed ? 'Ver menos' : 'Ver más';
}

window.toggleRecommendationText = function() { toggleRec('rec-content', 'rec-toggle-btn'); };
window.toggleVideosRecommendationText = function() { toggleRec('rec-videos-content', 'rec-videos-toggle-btn'); };
window.toggleEvalRecommendationText = function() { toggleRec('rec-eval-content', 'rec-eval-toggle-btn'); };