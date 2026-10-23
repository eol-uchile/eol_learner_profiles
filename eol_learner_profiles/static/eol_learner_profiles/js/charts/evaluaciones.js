import { showTooltip, moveTooltip, hideTooltip, applyRecommendationCollapse } from '../utils/helpers.js';
import { dataCalificaciones, DATA_EVALUACIONES_TIEMPO } from '../mock-data.js';

export function renderEvaluacionesChart(d3, view) {
    var container = document.getElementById('evaluaciones-chart');
    if (!container) return;
    container.innerHTML = '';

    if (view === 'calificaciones' && !dataCalificaciones.length) {
        container.innerHTML = '<p style="padding:20px; color:#666;">No hay evaluaciones disponibles aún.</p>';
        return;
    }

    var activeData = view === 'calificaciones' ? dataCalificaciones : DATA_EVALUACIONES_TIEMPO;

    if (view === 'calificaciones') {
        var contadoresTipo = {};
        activeData.forEach(function(d) {
            var letra = d.eval_type ? d.eval_type.charAt(0).toUpperCase() : 'E';
            if (!contadoresTipo[letra]) contadoresTipo[letra] = 0;
            contadoresTipo[letra]++;
            d.short_label = letra + contadoresTipo[letra]; 
        });
    }

    var margin = { top: 20, right: 20, bottom: 80, left: 60 }; 
    var height = 220; 
    var totalSvgHeight = height + margin.top + margin.bottom;
    
    var parentWidth = container.parentElement.clientWidth || 800;
    var idealMinWidth = activeData.length * 70;
    var width = Math.max(parentWidth, idealMinWidth) - margin.left - margin.right;
    
    container.style.overflowX = 'auto';
    container.style.overflowY = 'hidden';
    container.style.height = totalSvgHeight + 'px';
    var parentWrap = container.closest('.chart-scroll-wrap');
    if (parentWrap) parentWrap.style.height = 'auto';

    var svg = d3.select('#evaluaciones-chart').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', totalSvgHeight)
        .style('width', (width + margin.left + margin.right) + 'px')
        .style('height', totalSvgHeight + 'px');

    var chart = svg.append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
    var x = d3.scaleBand().domain(activeData.map(function (d, i) { return i; })).range([0, width]).padding(0.3);
    
    var maxValue = view === 'tiempo' ? d3.max(activeData, function(d) { return Math.max(d.max || 0, d.time_user || 0); }) * 1.1 : 100;
    if (!maxValue || maxValue === 0) maxValue = view === 'tiempo' ? 10 : 100;
    
    var yAxisLabel = view === 'tiempo' ? 'TIEMPO (MIN)' : 'CALIFICACIÓN (%)';
    var y = d3.scaleLinear().domain([0, maxValue]).nice().range([height, 0]);

    chart.append('g').attr('class', 'grid').call(d3.axisLeft(y).ticks(5).tickSize(-width).tickFormat('')).selectAll('line').style('stroke', '#eef2f5').style('stroke-opacity', '0.7');
    chart.selectAll('.grid path').style('stroke-width', '0');
    chart.append('g').attr('class', 'chart-axis').call(d3.axisLeft(y).ticks(5));
    chart.append('g').attr('class', 'chart-axis').attr('transform', 'translate(0,' + height + ')').call(d3.axisBottom(x).tickFormat(function (i) { return activeData[i].short_label; }));
    chart.append('text').attr('transform', 'rotate(-90)').attr('y', -margin.left + 15).attr('x', -height / 2).attr('dy', '1em').style('text-anchor', 'middle').style('font-size', '11px').style('fill', '#666').text(yAxisLabel);

    function getEvalTooltipHtml(d) {
        var label = view === 'calificaciones' ? ((d.eval_type ? d.eval_type + ': ' : '') + d.name) : d.name;
        var valTu = view === 'calificaciones' ? d.score_user + '%' : d.time_user.toFixed(1) + ' min';
        var valMedia = view === 'calificaciones' ? d.score_median + '%' : d.median.toFixed(1) + ' min';
        return '<strong>' + label + '</strong><br>Tú: ' + valTu + '<br>Mediana del curso: ' + valMedia;
    }

    if (view === 'calificaciones') {
        chart.selectAll('.evaluaciones-bar').data(activeData).enter().append('rect')
            .attr('class', 'evaluaciones-bar').attr('x', function (d, i) { return x(i); })
            .attr('y', function (d) { return y(d.score_user); })
            .attr('width', x.bandwidth()).attr('height', function (d) { return height - y(d.score_user); }).attr('rx', 1).style('cursor', 'pointer')
            .on('mouseover touchstart', function(e, d) { showTooltip(e, getEvalTooltipHtml(d)); })
            .on('mousemove touchmove', moveTooltip)
            .on('mouseout touchend', hideTooltip);

        chart.selectAll('.chart-average').data(activeData).enter().append('rect')
            .attr('class', 'chart-average').attr('x', function (d, i) { return x(i) - 2; }).attr('y', function (d) { return y(d.score_median) - 3; })
            .attr('width', x.bandwidth() + 4).attr('height', 6).attr('rx', 2).style('pointer-events', 'none').attr('fill', '#5d5d5d');
            
    } else {
        var boxGroup = chart.selectAll('.box-group').data(activeData).enter().append('g').attr('class', 'box-group').style('cursor', 'pointer')
            .on('mouseover touchstart', function(e, d) { showTooltip(e, getEvalTooltipHtml(d)); })
            .on('mousemove touchmove', moveTooltip)
            .on('mouseout touchend', hideTooltip);

        boxGroup.append('line').attr('x1', function(d, i) { return x(i) + x.bandwidth() / 2; }).attr('x2', function(d, i) { return x(i) + x.bandwidth() / 2; }).attr('y1', function(d) { return y(d.min); }).attr('y2', function(d) { return y(d.q1); }).attr('stroke', '#7a7a7a').attr('stroke-width', 4);
        boxGroup.append('line').attr('x1', function(d, i) { return x(i) + x.bandwidth() / 2; }).attr('x2', function(d, i) { return x(i) + x.bandwidth() / 2; }).attr('y1', function(d) { return y(d.q3); }).attr('y2', function(d) { return y(d.max); }).attr('stroke', '#d9d9d9').attr('stroke-width', 4);
        boxGroup.append('rect').attr('x', function (d, i) { return x(i); }).attr('y', function (d) { return y(d.median); }).attr('width', x.bandwidth()).attr('height', function (d) { return y(d.q1) - y(d.median); }).attr('fill', '#7a7a7a');
        boxGroup.append('rect').attr('x', function (d, i) { return x(i); }).attr('y', function (d) { return y(d.q3); }).attr('width', x.bandwidth()).attr('height', function (d) { return y(d.median) - y(d.q3); }).attr('fill', '#d9d9d9');
        boxGroup.append('rect').attr('x', function (d, i) { return x(i); }).attr('y', function (d) { return y(d.time_user) - 3; }).attr('width', x.bandwidth()).attr('height', 6).attr('rx', 2).attr('fill', '#c67b9c');
    }
    applyRecommendationCollapse('rec-eval-content', 'rec-eval-toggle-btn');
}