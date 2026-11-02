import { renderChart } from './charts/completitud.js';
import { renderEvaluacionesChart } from './charts/evaluaciones.js';
import { renderVideosChart } from './charts/videos.js';

let globalD3 = null;
let currentCompletitudView = 'chapter';
let currentNavigationView = 'chapter';
let currentEvaluacionesView = 'calificaciones';

function setupToggles(d3) {
    var buttons = document.querySelectorAll('.chart-toggle .toggle-btn:not(#btn-view-porcentaje):not(#btn-view-tiempo)');
    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            var view = button.getAttribute('data-view');
            var target = button.getAttribute('data-target');
            
            if (target === 'completitud') currentCompletitudView = view;
            else if (target === 'navigation') currentNavigationView = view;
            else if (target === 'evaluaciones') currentEvaluacionesView = view;
            
            var groupButtons = document.querySelectorAll('.view-toggle-' + target + ' .toggle-btn');
            groupButtons.forEach(function (btn) { btn.classList.remove('active'); });
            button.classList.add('active');
            
            if (target === 'evaluaciones') renderEvaluacionesChart(d3, view);
            else renderChart(d3, target, view);
        });
    });
}

function renderMetricsBar(metricas) {
    var container = document.getElementById('srl-metrics-bar');
    if (!container || !metricas || metricas.length === 0) return;

    var htmlItems = '';
    var htmlTooltips = '';

    metricas.forEach(function(metric) {
        htmlItems += '<div class="metric-item"><span class="metric-value">' + metric.value + (metric.unit || '') + '</span><div class="metric-details"><span class="metric-label">' + metric.label + '</span></div></div>';
        if (metric.tooltip) {
            htmlTooltips += '<li><strong>' + metric.label + ':</strong> ' + metric.tooltip + '</li>';
        }
    });

    container.innerHTML = htmlItems + 
        '<div class="metrics-info-container"><button class="tooltip-trigger" aria-label="Información sobre las métricas">ⓘ</button>' +
        '<div class="tooltip-box" role="tooltip"><strong>Información de métricas:</strong><ul class="metrics-info-list">' + 
        htmlTooltips + '</ul></div></div>';
}

// Resumen
if (typeof window.metricasData !== 'undefined') {
    renderMetricsBar(window.metricasData);
}

// Gráficos
import('https://cdn.jsdelivr.net/npm/d3@7/+esm').then(function (d3Module) {
    globalD3 = d3Module;
    renderChart(globalD3, 'completitud', currentCompletitudView);
    renderChart(globalD3, 'navigation', currentNavigationView);
    renderEvaluacionesChart(globalD3, currentEvaluacionesView);
    renderVideosChart();
    setupToggles(globalD3);
}).catch(function (error) {
    console.error('No se pudo cargar D3:', error);
});

// Responsive
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        if (globalD3) {
            renderChart(globalD3, 'completitud', currentCompletitudView);
            renderChart(globalD3, 'navigation', currentNavigationView);
            renderEvaluacionesChart(globalD3, currentEvaluacionesView);
        }
    }, 250);
});