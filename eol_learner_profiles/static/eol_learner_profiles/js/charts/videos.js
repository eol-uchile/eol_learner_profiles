import { formatTime, showTooltip, moveTooltip, hideTooltip, applyRecommendationCollapse } from '../utils/helpers.js';
import { DATA_VIDEOS } from '../mock-data.js';

export function renderVideosChart() {
    var container = document.getElementById('videos-accordion-container');
    if (!container) return;

    if(!DATA_VIDEOS || DATA_VIDEOS.length === 0) {
        container.innerHTML = '<p style="padding:20px; color:#666;">No hay datos de video para mostrar.</p>';
        return;
    }

    var htmlString = '';
    var chevronSvg = '<svg class="chevron-icon" viewBox="0 0 24 24"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/></svg>';

    DATA_VIDEOS.forEach(function(modulo, index) {
        var isOpen = index === 0 ? 'open' : '';
        var valUser = Math.min(Math.max(modulo.progress_user || 0, 0), 100);
        var valMedia = Math.min(Math.max(modulo.progress_median || 0, 0), 100);
        var labelLeft = '0%';
        var labelRight = '100%';
        var timeUserStr = formatTime(modulo.time_user * 60);
        var timeMedStr = formatTime(modulo.time_median * 60);

        htmlString += '<details class="video-module-details" ' + isOpen + '>';
        htmlString += '<summary class="video-module-summary">' + chevronSvg;
        htmlString += '<div class="video-title">' + modulo.title + '</div>';
        htmlString += '<div class="video-bar-wrapper">';
        
        var tooltipAttr = 'data-name="' + modulo.title + '" ' +
                          'data-tu="' + Math.round(valUser) + '%" ' +
                          'data-media="' + Math.round(valMedia) + '%" ' +
                          'data-inter-user="' + Math.round(modulo.inter_user || 0) + '" ' +
                          'data-inter-media="' + Math.round(modulo.inter_median || 0) + '" ' +
                          'data-tiempo-user="' + timeUserStr + '" ' +
                          'data-tiempo-media="' + timeMedStr + '"';

        htmlString += '  <div class="video-bar-bg tooltip-target" ' + tooltipAttr + '>';
        htmlString += '    <div class="video-bar-fill" style="width: ' + valUser + '%;"></div>';
        htmlString += '    <div class="video-median-marker" style="left: ' + valMedia + '%;"></div>';
        htmlString += '  </div>';
        htmlString += '  <div class="video-bar-labels"><span>' + labelLeft + '</span><span>' + labelRight + '</span></div>';
        htmlString += '</div><div class="video-meta">(' + modulo.videos_count + ' videos)</div></summary>';
        
        if (modulo.items && modulo.items.length > 0) {
            htmlString += '<div class="video-items-list">';
            modulo.items.forEach(function(video) {
                var vUser = Math.min(Math.max(video.progress_user || 0, 0), 100);
                var vMedia = Math.min(Math.max(video.progress_median || 0, 0), 100);
                var vTimeUserStr = formatTime((video.time_user || 0) * 60);
                var vTimeMedStr = formatTime((video.time_median || 0) * 60);

                var vTooltipAttr = 'data-name="' + video.title + '" ' +
                                   'data-tu="' + Math.round(vUser) + '%" ' +
                                   'data-media="' + Math.round(vMedia) + '%" ' +
                                   'data-inter-user="' + Math.round(video.inter_user || 0) + '" ' +
                                   'data-inter-media="' + Math.round(video.inter_median || 0) + '" ' +
                                   'data-tiempo-user="' + vTimeUserStr + '" ' +
                                   'data-tiempo-media="' + vTimeMedStr + '"';

                htmlString += '<div class="video-item-row"><div class="video-title">' + video.title + '</div>';
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
    
    document.querySelectorAll('#videos-accordion-container .tooltip-target').forEach(function(target) {
        function handleHover(e) {
            var name = target.getAttribute('data-name');
            var tuPct = target.getAttribute('data-tu');
            var medPct = target.getAttribute('data-media');
            var interUser = target.getAttribute('data-inter-user');
            var interMed = target.getAttribute('data-inter-media');
            var tiempoUser = target.getAttribute('data-tiempo-user');
            var tiempoMed = target.getAttribute('data-tiempo-media');

            var html = '<strong>' + name + '</strong><br>' +
                       '📊 Avance: Tú: ' + tuPct + ' | Mediana: ' + medPct + '<br>' +
                       '🖱️ Interacciones: ' + interUser + ' | Mediana: ' + interMed + '<br>' +
                       '⏱️ Tiempo visualizado: ' + tiempoUser + ' | Mediana: ' + tiempoMed;
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