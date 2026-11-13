document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.getElementById('markdown_content');
    const previewContainer = document.getElementById('preview-container');
    if (!textarea || !previewContainer) return;

    const previewUrl = previewContainer.dataset.previewUrl;
    const csrfToken = previewContainer.dataset.csrfToken;

    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function updatePreview() {
        const formData = new FormData();
        formData.append('markdown_content', textarea.value);
        formData.append('csrfmiddlewaretoken', csrfToken);

        fetch(previewUrl, { method: 'POST', body: formData })
            .then(r => r.json())
            .then(data => { if (data.success) { renderPreviewHtml(data.parsed); } })
            .catch(err => console.error("Error actualizando preview", err));
    }

    function renderQuestion(q) {
        let html = '<div class="preview-question">';
        if (q.type === 'likert_matrix') {
            html += '<table class="likert-table"><thead><tr><th>Enunciado</th>';
            (q.scale || []).forEach(s => { html += '<th>' + esc(s) + '</th>'; });
            html += '</tr></thead><tbody>';
            (q.rows || []).forEach(r => {
                html += '<tr><td>' + esc(r.statement) + '</td>';
                (q.scale || []).forEach(() => { html += '<td><input type="radio" disabled></td>'; });
                html += '</tr>';
            });
            html += '</tbody></table>';
        } else {
            html += '<p><strong>' + esc(q.text) + '</strong></p>';
            (q.options || []).forEach(opt => {
                const inputType = q.type === 'checkbox' ? 'checkbox' : 'radio';
                html += '<div><label><input type="' + inputType + '" disabled> ' + esc(opt.text) + '</label>';
                if (opt.has_other_text) {
                    html += ' <input type="text" placeholder="Especificar..." disabled '
                          + 'style="width:200px;display:inline-block;margin-left:0.5rem;">';
                }
                html += '</div>';
            });
        }
        return html + '</div>';
    }

    function renderPreviewHtml(parsed) {
        const pages = (parsed && parsed.pages) || [];
        const total = pages.length;
        if (!total || pages.every(p => !p.blocks || !p.blocks.length)) {
            previewContainer.innerHTML = '<p>No hay preguntas definidas.</p>';
            return;
        }

        let html = '';
        pages.forEach((page, i) => {
            if (i > 0) {
                html += '<div class="preview-pagebreak">&mdash;&mdash; Salto de página &mdash;&mdash;</div>';
            }
            if (total > 1) {
                html += '<p class="preview-pagelabel">Página ' + (i + 1) + ' de ' + total + '</p>';
            }
            html += '<div class="preview-card">';
            (page.blocks || []).forEach(block => {
                if (block.kind === 'section') {
                    html += '<h3>' + esc(block.title)
                          + (block.continued ? ' <small>(continuación)</small>' : '') + '</h3>';
                } else if (block.kind === 'question') {
                    html += renderQuestion(block.q);
                }
            });
            html += '</div>';
        });
        previewContainer.innerHTML = html;
    }

    textarea.addEventListener('input', updatePreview);
    updatePreview();
});
