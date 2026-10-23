import { formatTime, getXLabel, showTooltip, moveTooltip, hideTooltip, applyRecommendationCollapse } from '../utils/helpers.js';
import { DATA_COMPLETITUD, DATA_NAVEGACION } from '../mock-data.js';

export function renderChart(d3, chartType, view) {
    var containerId = chartType === 'completitud' ? 'completitud-chart' : 'navigation-chart';
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    var data = chartType === 'completitud' ? DATA_COMPLETITUD[view] : DATA_NAVEGACION[view];
    if(!data || data.length === 0) {
        container.innerHTML = '<p style="padding:20px; color:#666;">No hay datos disponibles para esta vista.</p>';
        return;
    }

    var margin = { top: 20, right: 20, bottom: view === 'chapter' ? 80 : 60, left: 60 };
    var height = 200;
    
    var parentWidth = container.parentElement.clientWidth || 800;
    var idealMinWidth = (view === 'chapter') ? data.length * 60 : data.length * 80;
    var containerWidth = Math.max(parentWidth, idealMinWidth);
    var width = containerWidth - margin.left - margin.right;

    var svg = d3.select('#' + containerId).append('svg')
        .attr('width', containerWidth)
        .attr('height', height + margin.top + margin.bottom);

    var chart = svg.append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
    var labels = data.map(function (d) { return getXLabel(d, view); });
    var x = d3.scaleBand().domain(labels).range([0, width]).padding(0.2);

    var isCompletitud = chartType === 'completitud';
    var maxValue = isCompletitud ? 100 : d3.max(data, function(d) { return Math.max(d.individual_time, d.average_time) / 60; }) * 1.15;
    if (!maxValue || maxValue === 0) maxValue = isCompletitud ? 100 : 1; 

    var yAxisLabel = isCompletitud ? 'AVANCE (%)' : 'TIEMPO (H)';
    var colorBarra = isCompletitud ? 'completitud-bar' : 'navigation-bar';
    var lineColor = isCompletitud ? '#00a676' : '#087db2';
    var y = d3.scaleLinear().domain([0, maxValue]).nice().range([height, 0]);

    chart.append('g').attr('class', 'grid')
        .call(d3.axisLeft(y).ticks(5).tickSize(-width).tickFormat(''))
        .selectAll('line').style('stroke', '#eef2f5').style('stroke-opacity', '0.7');
    chart.selectAll('.grid path').style('stroke-width', '0');
    chart.append('g').attr('class', 'chart-axis').call(d3.axisLeft(y).ticks(5).tickFormat(function (d) { return isCompletitud ? d : d.toFixed(1); }));

    var xAxis = chart.append('g').attr('class', 'chart-axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(d3.axisBottom(x).tickFormat(function(label) {
            return label.length > 11 ? label.substring(0, 9) + '...' : label;
        }));

    chart.append('text').attr('transform', 'rotate(-90)').attr('y', -margin.left + 15).attr('x', -height / 2)
        .attr('dy', '1em').style('text-anchor', 'middle').style('font-size', '11px').style('fill', '#666').text(yAxisLabel);

    function getTooltipHtml(d) {
        var label = view === 'week' ? (d.date_label || 'Semana ' + d.week) : d.name;
        var valTu = isCompletitud ? d.individual_time.toFixed(1) + '%' : formatTime(d.individual_time);
        var valMedia = isCompletitud ? d.average_time.toFixed(1) + '%' : formatTime(d.average_time);
        return '<strong>' + label + '</strong><br>Tú: ' + valTu + '<br>Mediana del curso: ' + valMedia;
    }

    if (view === 'week') {
        var lineTu = d3.line().x(function (d) { return x(getXLabel(d, view)) + x.bandwidth() / 2; }).y(function (d) { return isCompletitud ? y(d.individual_time) : y(d.individual_time / 60); });
        var lineMedia = d3.line().x(function (d) { return x(getXLabel(d, view)) + x.bandwidth() / 2; }).y(function (d) { return isCompletitud ? y(d.average_time) : y(d.average_time / 60); });

        if (isCompletitud) {
            var areaMediana = d3.area().x(function (d) { return x(getXLabel(d, view)) + x.bandwidth() / 2; }).y0(height).y1(function (d) { return y(d.average_time); });
            var areaTu = d3.area().x(function (d) { return x(getXLabel(d, view)) + x.bandwidth() / 2; }).y0(height).y1(function (d) { return y(d.individual_time); });
            chart.append('path').datum(data).attr('fill', '#5d5d5d').attr('fill-opacity', 0.15).attr('d', areaMediana).style('pointer-events', 'none');
            chart.append('path').datum(data).attr('fill', lineColor).attr('fill-opacity', 0.15).attr('d', areaTu).style('pointer-events', 'none');
        }

        chart.append('path').datum(data).attr('fill', 'none').attr('stroke', '#5d5d5d').attr('stroke-width', 2).attr('stroke-dasharray', '5,5').attr('d', lineMedia);
        chart.append('path').datum(data).attr('fill', 'none').attr('stroke', lineColor).attr('stroke-width', 3).attr('d', lineTu);

        chart.selectAll('.dot-punto').data(data).enter().append('circle')
            .attr('cx', function (d) { return x(getXLabel(d, view)) + x.bandwidth() / 2; }).attr('cy', function (d) { return isCompletitud ? y(d.individual_time) : y(d.individual_time / 60); })
            .attr('r', 6).attr('fill', lineColor).style('cursor', 'pointer')
            .on('mouseover touchstart', function(e, d) { showTooltip(e, getTooltipHtml(d)); })
            .on('mousemove touchmove', moveTooltip)
            .on('mouseout touchend', hideTooltip);
    } else {
        chart.selectAll('.' + colorBarra).data(data).enter().append('rect')
            .attr('class', colorBarra).attr('x', function (d) { return x(getXLabel(d, view)); })
            .attr('y', function (d) { return isCompletitud ? y(d.individual_time) : y(d.individual_time / 60); })
            .attr('width', x.bandwidth()).attr('height', function (d) { return height - (isCompletitud ? y(d.individual_time) : y(d.individual_time / 60)); })
            .attr('rx', 1).style('cursor', 'pointer')
            .on('mouseover touchstart', function(e, d) { showTooltip(e, getTooltipHtml(d)); })
            .on('mousemove touchmove', moveTooltip)
            .on('mouseout touchend', hideTooltip);

        chart.selectAll('.chart-average').data(data).enter().append('rect')
            .attr('class', 'chart-average').attr('x', function (d) { return x(getXLabel(d, view)) - 2; }).attr('y', function (d) { return (isCompletitud ? y(d.average_time) : y(d.average_time / 60)) - 3; })
            .attr('width', x.bandwidth() + 4).attr('height', 6).attr('rx', 2).style('pointer-events', 'none');
    }

    applyRecommendationCollapse('rec-content', 'rec-toggle-btn');
}