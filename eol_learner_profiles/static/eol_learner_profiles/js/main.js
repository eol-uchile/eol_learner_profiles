import { procesarDatos } from './mock-data.js';
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

// 1. Inicializar
procesarDatos();

// 2. Importar D3
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

// 3. Responsive
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