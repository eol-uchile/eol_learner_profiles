export const DATA_COMPLETITUD = { week: [], chapter: [] };
export const DATA_NAVEGACION = { week: [], chapter: [] };
export const DATA_VIDEOS = [];
export const DATA_EVALUACIONES_TIEMPO = [];
export let dataCalificaciones = [];

export function procesarDatos() {
    // Leer variables globales inyectadas por Mako en el HTML
    var userNavWeek = typeof window.navigationWeek !== 'undefined' ? window.navigationWeek : [];
    var userNavChapter = typeof window.navigationChapter !== 'undefined' ? window.navigationChapter : [];
    var userVideos = typeof window.videosData !== 'undefined' ? window.videosData : [];
    var sysAgregaciones = typeof window.agregacionesData !== 'undefined' ? window.agregacionesData : { MEDIAN: {} };
    dataCalificaciones = (typeof window.evaluacionesData !== 'undefined' && window.evaluacionesData) ? window.evaluacionesData : [];

    // Asignación de mediana aleatoria (0-100) para calificaciones
    dataCalificaciones.forEach(function(d) {
        d.score_median = Math.floor(Math.random() * 101); 
    });

    var medianNavWeek = sysAgregaciones.MEDIAN?.metrics_per_week || [];
    var medianNavChapter = sysAgregaciones.MEDIAN?.metrics_per_structure || [];
    var medianVideos = sysAgregaciones.MEDIAN?.metrics_per_video || [];

    // --- Semanas ---
    function getMedianWeek(weekNum, key) {
        var found = medianNavWeek.find(function(m) { return m.week === weekNum; });
        return found ? (parseFloat(found[key]) || 0) : 0;
    }

    userNavWeek.forEach(function(d) {
        var compMed = getMedianWeek(d.week, 'COMPLETITUD_POR_SEMANA');
        var navMed = getMedianWeek(d.week, 'TIEMPO_NAVEGACION_POR_SEMANA');

        DATA_COMPLETITUD.week.push({
            week: d.week, date_label: 'Semana ' + d.week,
            individual_time: (parseFloat(d.COMPLETITUD_POR_SEMANA) || 0) * 100,
            average_time: compMed * 100
        });

        DATA_NAVEGACION.week.push({
            week: d.week, date_label: 'Semana ' + d.week,
            individual_time: (parseFloat(d.TIEMPO_NAVEGACION_POR_SEMANA) || 0) / 60,
            average_time: navMed / 60
        });
    });

    // --- Modulos ---
    function aggregateChapters(dataArr) {
        var groups = {};
        dataArr.forEach(function(d) {
            if (!d.chapter_name) return;
            var cName = d.chapter_name;
            if (!groups[cName]) {
                groups[cName] = { name: cName, vis_time: 0, dur_time: 0, order: d.chapter_order || 99 };
            }
            groups[cName].vis_time += parseFloat(d.visualization_time) || 0;
            groups[cName].dur_time += parseFloat(d.vertical_duration) || 0;
        });
        return Object.values(groups).sort(function(a, b) { return a.order - b.order; });
    }

    var aggUserChapter = aggregateChapters(userNavChapter);
    var aggMedianChapter = aggregateChapters(medianNavChapter);

    aggUserChapter.forEach(function(uCh) {
        var mCh = aggMedianChapter.find(function(m) { return m.name === uCh.name; }) || { vis_time: 0, dur_time: 1 };
        var compUser = uCh.dur_time > 0 ? (uCh.vis_time / uCh.dur_time) * 100 : 0;
        var compMed = mCh.dur_time > 0 ? (mCh.vis_time / mCh.dur_time) * 100 : 0;
        
        DATA_COMPLETITUD.chapter.push({ name: uCh.name, individual_time: Math.min(compUser, 100), average_time: Math.min(compMed, 100) });
        DATA_NAVEGACION.chapter.push({ name: uCh.name, individual_time: uCh.vis_time / 60, average_time: mCh.vis_time / 60 });
    });

    // --- Videos ---
    var videoGroups = {};
    userVideos.forEach(function(v) {
        var cName = v.chapter_name || "Otros Videos";
        if (!videoGroups[cName]) {
            videoGroups[cName] = {
                title: cName, progress_user: 0, progress_median: 0,
                time_user: 0, time_median: 0, time_total: 0,
                videos_count: 0, items: [], order: v.chapter_order || 99
            };
        }
        var vMed = medianVideos.find(function(mv) { return mv.vertical_name === v.vertical_name && mv.chapter_name === v.chapter_name; }) || {};
        var userTime = (parseFloat(v.visualization_time) || 0) / 60;
        var medTime = (parseFloat(vMed.visualization_time) || 0) / 60;
        var totalTime = (parseFloat(v.video_duration) || 120) / 60;

        videoGroups[cName].items.push({
            title: (v.vertical_name || "Video") + (v.block_name ? " - " + v.block_name : ""),
            progress_user: (parseFloat(v.visualization_percent) || 0) * 100,
            progress_median: (parseFloat(vMed.visualization_percent) || 0) * 100,
            inter_user: parseFloat(v.play_count || 0) + parseFloat(v.pause_count || 0),
            inter_median: parseFloat(vMed.play_count || 0) + parseFloat(vMed.pause_count || 0),
            time_user: userTime, time_median: medTime, time_total: totalTime
        });
        videoGroups[cName].videos_count++;
        videoGroups[cName].time_user += userTime;
        videoGroups[cName].time_median += medTime;
        videoGroups[cName].time_total += totalTime;
    });

    Object.values(videoGroups).forEach(function(g) {
        if(g.videos_count > 0) {
            var sumUserProg = 0, sumMedProg = 0;
            g.items.forEach(function(i) { sumUserProg += i.progress_user; sumMedProg += i.progress_median; });
            g.progress_user = sumUserProg / g.videos_count;
            g.progress_median = sumMedProg / g.videos_count;
        }
        DATA_VIDEOS.push(g);
    });
    DATA_VIDEOS.sort(function(a,b) { return a.order - b.order; });

    // --- Evaluaciones de Tiempo ---
    var sysP33Chapter = sysAgregaciones.P_33?.metrics_per_structure || [];
    var sysP66Chapter = sysAgregaciones.P_66?.metrics_per_structure || [];
    var evaluacionesUsuario = userNavChapter.filter(function(d) { return d.graded === true || d.graded === 'True'; });

    evaluacionesUsuario.forEach(function(ev, index) {
        var name = ev.sequential_name || 'Evaluación ' + (index + 1);
        var mEv = medianNavChapter.find(function(m) { return m.sequential_name === name; }) || {};
        var p33Ev = sysP33Chapter.find(function(m) { return m.sequential_name === name; }) || {};
        var p66Ev = sysP66Chapter.find(function(m) { return m.sequential_name === name; }) || {};

        var tUser = (parseFloat(ev.visualization_time) || 0) / 60;
        var tMed = (parseFloat(mEv.visualization_time) || 0) / 60;
        var tQ1 = (parseFloat(p33Ev.visualization_time) || 0) / 60;
        var tQ3 = (parseFloat(p66Ev.visualization_time) || 0) / 60;

        if(!tMed && tUser) tMed = tUser;
        if(!tQ1) tQ1 = tMed * 0.7;
        if(!tQ3) tQ3 = tMed * 1.3;

        DATA_EVALUACIONES_TIEMPO.push({
            name: name, short_label: 'E' + (index + 1),
            time_user: tUser, median: tMed, q1: tQ1, q3: tQ3,
            min: tQ1 * 0.5, max: tQ3 * 1.5
        });
    });
}