import { formatTime, showTooltip, moveTooltip, hideTooltip, applyRecommendationCollapse } from '../utils/helpers.js';

export function renderVideosChart() {
    var container = document.getElementById('videos-accordion-container');
    if (!container) return;

    var rawVideos = [];
    if (window.videosData && window.videosData.grouped_data && window.videosData.grouped_data.length > 0) {
            // Datos API
        if (window.videosData.grouped_data[0].chapters) {
            rawVideos = window.videosData.grouped_data[0].chapters;
        } else {
            // Datos json
            rawVideos = window.videosData.grouped_data;
        }
    }

    if(!rawVideos || rawVideos.length === 0) {
        return;
    }

    var htmlString = '';
    var chevronSvg = '<svg class="chevron-icon" viewBox="0 0 24 24"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/></svg>';

    rawVideos.forEach(function(modulo, index) {
        var isOpen = index === 0 ? 'open' : '';
        
        // --- DATOS DEL MÓDULO (Desplegable general) ---
        var valUser = Math.min(Math.max(modulo.average_visualization_rate || modulo.visualization_rate || 0, 0), 100);
        var valMedia = Math.min(Math.max(modulo.visualization_rate_median || 0, 0), 100); 
        
        var timeUserStr = formatTime(modulo.sum_interaction_time || 0);
        var cantidadVideosModulo = (modulo.videos && Array.isArray(modulo.videos)) ? modulo.videos.length : 0;

        htmlString += '<details class="video-module-details" ' + isOpen + '>';
        htmlString += '<summary class="video-module-summary">' + chevronSvg;
        htmlString += '<div class="video-title">' + (modulo.name || 'Módulo') + '</div>';
        htmlString += '<div class="video-bar-wrapper">';
        
        var tooltipAttr = 'data-name="' + (modulo.name || 'Módulo') + '" ' +
                          'data-tu="' + Math.round(valUser) + '%" ' +
                          'data-media="' + Math.round(valMedia) + '%" ' +
                          'data-tiempo-user="' + timeUserStr + '" ';

        htmlString += '  <div class="video-bar-bg tooltip-target" ' + tooltipAttr + '>';
        htmlString += '    <div class="video-bar-fill" style="width: ' + valUser + '%;"></div>';
        if (valMedia > 0) {
            htmlString += '    <div class="video-median-marker" style="left: ' + valMedia + '%;"></div>';
        }
        htmlString += '  </div>';
        htmlString += '  <div class="video-bar-labels"><span>0%</span><span>100%</span></div>';
        htmlString += '</div><div class="video-meta">(' + cantidadVideosModulo + ' videos)</div></summary>';
        
        // Dentro del desplegable
        if (cantidadVideosModulo > 0) {
            htmlString += '<div class="video-items-list">';
            modulo.videos.forEach(function(video) {
                var vUser = Math.min(Math.max(video.visualization_rate_individual || 0, 0), 100);
                var vMedia = Math.min(Math.max(video.visualization_rate_median || 0, 0), 100); 
                
                var vTimeUserStr = formatTime(video.interaction_time || 0);

                var sumInteraccionesUser = (video.play_count_individual || 0) + (video.pause_count_individual || 0) + (video.seek_count_individual || 0);
                var sumInteraccionesMedia = (video.play_count_median || 0) + (video.pause_count_median || 0) + (video.seek_count_median || 0);

                var vTooltipAttr = 'data-name="' + (video.name || 'Video') + '" ' +
                                   'data-tu="' + Math.round(vUser) + '%" ' +
                                   'data-media="' + Math.round(vMedia) + '%" ' +
                                   'data-inter-user="' + Math.round(sumInteraccionesUser) + '" ' +
                                   'data-inter-media="' + Math.round(sumInteraccionesMedia) + '" ' +
                                   'data-tiempo-user="' + vTimeUserStr + '" ';

                htmlString += '<div class="video-item-row"><div class="video-title">' + (video.name || 'Video') + '</div>';
                htmlString += '  <div class="video-bar-wrapper">';
                htmlString += '    <div class="video-bar-bg tooltip-target" ' + vTooltipAttr + '>';
                htmlString += '      <div class="video-bar-fill" style="width: ' + vUser + '%;"></div>';
                htmlString += '      <div class="video-median-marker" style="left: ' + vMedia + '%;"></div>';
                htmlString += '    </div><div class="video-bar-labels"><span>0%</span><span>100%</span></div>';
                htmlString += '  </div></div>';
            });
            htmlString += '</div>';
        }
        htmlString += '</details>';
    });

    container.innerHTML = htmlString;
    
    // tooltips
    document.querySelectorAll('#videos-accordion-container .tooltip-target').forEach(function(target) {
        function handleHover(e) {
            var name = target.getAttribute('data-name');
            var tuPct = target.getAttribute('data-tu');
            var medPct = target.getAttribute('data-media');
            var interUser = target.getAttribute('data-inter-user');
            var interMed = target.getAttribute('data-inter-media');
            var tiempoUser = target.getAttribute('data-tiempo-user');

            var html = '<strong>' + name + '</strong><br>' +
                       '📊 Avance: Tú: ' + tuPct + ' | Mediana: ' + medPct + '<br>';
            
            if (interUser !== null) {
                html += '🖱️ Interacciones: Tú: ' + interUser + ' | Mediana: ' + interMed + '<br>';
            }
            
            html += '⏱️ Tiempo visualizado: ' + tiempoUser;
            
            showTooltip(e, html);
        }
        target.addEventListener('mouseover', handleHover);
        target.addEventListener('touchstart', function(e) { handleHover(e.touches[0]); });
        target.addEventListener('mousemove', moveTooltip);
        target.addEventListener('touchmove', function(e) { moveTooltip(e.touches[0]); });
        target.addEventListener('mouseout', hideTooltip);
        target.addEventListener('touchend', hideTooltip);
    });

    applyRecommendationCollapse('rec-videos-content', 'rec-videos-toggle-btn');
}