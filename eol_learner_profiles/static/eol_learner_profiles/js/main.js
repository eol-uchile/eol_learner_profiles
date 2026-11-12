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
    var configData = window.resumenConfig || {};

    var htmlItems = '';
    var htmlTooltips = '';

    metricas.forEach(function(metric) {
        var config = configData[metric.key] || { label: metric.key, unit: '', tooltip: '' };
        
        htmlItems += '<div class="metric-item"><span class="metric-value">' + metric.value + config.unit + '</span><div class="metric-details"><span class="metric-label">' + config.label + '</span></div></div>';
        
        if (config.tooltip) {
            htmlTooltips += '<li><strong>' + config.label + ':</strong> ' + config.tooltip + '</li>';
        }
    });

    var tooltipHtml = '';
    if (htmlTooltips !== '') {
        tooltipHtml = '<div class="metrics-info-container"><button class="tooltip-trigger" aria-label="Información sobre las métricas">ⓘ</button>' +
        '<div class="tooltip-box" role="tooltip"><strong>Información de métricas:</strong><ul class="metrics-info-list">' + 
        htmlTooltips + '</ul></div></div>';
    }

    container.innerHTML = htmlItems + tooltipHtml;
}

function loadScript(src) {
    return new Promise(function (resolve, reject) {
        var s = document.createElement('script');
        s.src = src;
        s.async = true;
        s.onload = resolve;
        s.onerror = reject;
        document.head.appendChild(s);
    });
}

// Resumen
if (typeof window.metricasData !== 'undefined') {
    renderMetricsBar(window.metricasData);
}

// Gráficos
loadScript('https://cdn.jsdelivr.net/npm/d3@7.9/dist/d3.min.js').then(function () {
    globalD3 = window.d3;
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