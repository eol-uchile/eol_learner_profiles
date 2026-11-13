/* eol_learner_profiles - pestaña "Recomendaciones".
 * Progresivo, sin dependencias:
 *   - encuesta paginada (Anterior / Siguiente / Enviar)
 *   - tarjeta de encuesta colapsable cuando ya fue respondida
 *   - modal de Configuración (sólo staff)
 *   - aviso suave si quedan filas Likert sin responder al enviar
 */
(function () {
    "use strict";

    function onReady(fn) {
        if (document.readyState !== "loading") { fn(); }
        else { document.addEventListener("DOMContentLoaded", fn); }
    }

    /* ---- encuesta paginada -------------------------------------------- */
    function setupPagedSurvey() {
        var form = document.getElementById("eol-lp-survey-form");
        if (!form) { return; }

        var pages = Array.prototype.slice.call(form.querySelectorAll(".eol-lp-survey-page"));
        var prev = form.querySelector(".eol-lp-nav-prev");
        var next = form.querySelector(".eol-lp-nav-next");
        var submit = form.querySelector(".eol-lp-nav-submit");
        var curLabel = form.querySelector(".eol-lp-nav-cur");
        var card = document.getElementById("eol-lp-survey");
        var idx = 0;

        function show(n) {
            idx = Math.max(0, Math.min(n, pages.length - 1));
            pages.forEach(function (p, i) { p.hidden = (i !== idx); });
            if (prev) { prev.hidden = (idx === 0); }
            var last = (idx === pages.length - 1);
            if (next) { next.hidden = last || pages.length <= 1; }
            if (submit) { submit.hidden = !last && pages.length > 1; }
            if (curLabel) { curLabel.textContent = String(idx + 1); }
            if (card && card.scrollIntoView) {
                card.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        }

        if (prev) { prev.addEventListener("click", function () { show(idx - 1); }); }
        if (next) { next.addEventListener("click", function () { show(idx + 1); }); }

        if (pages.length > 1) { show(0); }

        form.addEventListener("submit", function (event) {
            var missing = [];
            form.querySelectorAll(".ils-likert-table tbody tr").forEach(function (row) {
                row.classList.remove("ils-likert-row-missing");
                var inputs = row.querySelectorAll('input[type="radio"]');
                if (!inputs.length) { return; }
                var answered = Array.prototype.some.call(inputs, function (i) { return i.checked; });
                if (!answered) { missing.push(row); }
            });
            if (missing.length && !window.confirm(
                "Hay " + missing.length + " afirmación(es) sin responder. ¿Enviar de todas formas?"
            )) {
                event.preventDefault();
                missing.forEach(function (r) { r.classList.add("ils-likert-row-missing"); });
                // salta a la página de la primera fila sin responder
                var page = missing[0].closest(".eol-lp-survey-page");
                var pi = pages.indexOf(page);
                if (pi >= 0) { show(pi); }
                missing[0].scrollIntoView({ behavior: "smooth", block: "center" });
            }
        });
    }

    /* ---- tarjeta de encuesta colapsable ----------------------------- */
    function setupCollapsible() {
        var card = document.getElementById("eol-lp-survey");
        var toggle = card && card.querySelector(".eol-lp-survey-toggle");
        var body = document.getElementById("eol-lp-survey-body");
        if (!card || !toggle || !body) { return; }

        toggle.addEventListener("click", function () {
            var collapsed = card.classList.toggle("is-collapsed");
            body.hidden = collapsed;
            toggle.setAttribute("aria-expanded", String(!collapsed));
        });
    }

    /* ---- modal de configuración (staff) --------------------------- */
    function setupConfigModal() {
        var opener = document.getElementById("eol-lp-config-open");
        var modal = document.getElementById("eol-lp-config-modal");
        if (!opener || !modal) { return; }

        function open() {
            modal.classList.add("is-open");
            var dialog = modal.querySelector(".eol-lp-modal-dialog");
            if (dialog) { dialog.focus(); }
        }
        function close() { modal.classList.remove("is-open"); }

        opener.addEventListener("click", open);
        modal.querySelectorAll("[data-close]").forEach(function (el) {
            el.addEventListener("click", close);
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && modal.classList.contains("is-open")) { close(); }
        });
    }

    onReady(function () {
        setupPagedSurvey();
        setupCollapsible();
        setupConfigModal();
    });
})();
