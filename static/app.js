(() => {
    // DOM elements
    const passageBox = document.getElementById('passage-box');
    const passageTitle = document.getElementById('passage-title');
    const passageAuthor = document.getElementById('passage-author');
    const passageWordCount = document.getElementById('passage-word-count');
    const sourceLink = document.getElementById('source-link');
    const newPassageBtn = document.getElementById('new-passage-btn');

    const responseInput = document.getElementById('response-input');
    const responseWordCount = document.getElementById('response-word-count');
    const submitBtn = document.getElementById('submit-btn');
    const exportBtn = document.getElementById('export-btn');
    const exportFormat = document.getElementById('export-format');

    const feedbackCard = document.getElementById('feedback-card');
    const ratingEl = document.getElementById('rating');
    const scoreRing = document.getElementById('score-ring');
    const scoreValue = document.getElementById('score-value');
    const checklistEl = document.getElementById('checklist');
    const suggestionsEl = document.getElementById('feedback-card').querySelector('.suggestions ul');

    const SHIMMER_HTML = '<div class="shimmer" id="passage-shimmer"><span></span><span></span><span></span><span></span></div>';

    // State
    let currentPassage = null;
    let currentFeedback = null;

    function setLoading(isLoading) {
        newPassageBtn.disabled = isLoading;
        submitBtn.disabled = isLoading;
        if (isLoading) {
            passageBox.classList.add('is-loading');
            passageBox.innerHTML = SHIMMER_HTML;
        } else {
            passageBox.classList.remove('is-loading');
        }
    }

    function countWords(text) {
        return text.trim() ? text.trim().split(/\s+/).length : 0;
    }

    async function loadPassage() {
        setLoading(true);
        feedbackCard.classList.add('hidden');
        try {
            const res = await fetch('/api/random-passage');
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            const data = await res.json();
            currentPassage = data;
            currentFeedback = null;
            renderPassage(data);
        } catch (err) {
            console.error(err);
            passageBox.textContent = `Could not load a passage. ${err.message}`;
            passageTitle.textContent = 'Error';
            passageAuthor.textContent = '—';
            passageWordCount.textContent = '— words';
            sourceLink.href = 'https://www.gutenberg.org/';
        } finally {
            setLoading(false);
        }
    }

    function renderPassage(data) {
        // Small fade effect
        passageBox.style.opacity = '0';
        setTimeout(() => {
            passageBox.textContent = data.passage;
            passageTitle.textContent = data.title;
            passageAuthor.textContent = data.author;
            passageWordCount.textContent = `${data.word_count} words`;
            sourceLink.href = data.source_url;
            passageBox.style.opacity = '1';
        }, 150);
    }

    async function submitFeedback() {
        if (!currentPassage) {
            alert('Please load a passage first.');
            return;
        }
        const response = responseInput.value.trim();
        if (!response) {
            alert('Please write an analysis before submitting.');
            responseInput.focus();
            return;
        }

        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="btn-icon" aria-hidden="true">⟳</span> Analyzing…';
        try {
            const res = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ passage: currentPassage.passage, response }),
            });
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            const data = await res.json();
            currentFeedback = data;
            renderFeedback(data);
        } catch (err) {
            console.error(err);
            alert('Could not get feedback. ' + err.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }

    function renderFeedback(data) {
        feedbackCard.classList.remove('hidden');

        ratingEl.textContent = data.rating;
        scoreValue.textContent = `${data.passed}/${data.total}`;

        const angle = (data.passed / data.total) * 360;
        scoreRing.style.setProperty('--score-angle', `${angle}deg`);

        // Color the ring and top border by rating
        feedbackCard.style.borderTopColor = data.rating === 'Strong'
            ? 'var(--success)'
            : data.rating === 'Good'
                ? 'var(--warning)'
                : 'var(--danger)';

        checklistEl.innerHTML = '';
        let delay = 0;
        for (const key of Object.keys(data.checks)) {
            const item = data.checks[key];
            const li = document.createElement('li');
            li.className = item.passed ? 'pass' : 'fail';
            li.style.animationDelay = `${delay}ms`;
            li.innerHTML = `
                <span class="check-icon" aria-hidden="true">${item.passed ? '✓' : '!'}</span>
                <span class="check-label">${escapeHtml(item.label)}</span>
            `;
            checklistEl.appendChild(li);
            delay += 80;
        }

        suggestionsEl.innerHTML = '';
        for (const s of data.suggestions) {
            const li = document.createElement('li');
            li.textContent = s;
            suggestionsEl.appendChild(li);
        }

        feedbackCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function exportResponse() {
        if (!currentPassage) {
            alert('No passage to export. Load a passage first.');
            return;
        }
        const response = responseInput.value.trim();
        const format = exportFormat.value;
        const timestamp = new Date().toISOString();
        const filenameBase = `lit-passage-practice-${timestamp.slice(0, 10)}`;

        const payload = {
            title: currentPassage.title,
            author: currentPassage.author,
            source_url: currentPassage.source_url,
            passage: currentPassage.passage,
            passage_word_count: currentPassage.word_count,
            response,
            response_word_count: countWords(response),
            feedback: currentFeedback,
            exported_at: timestamp,
        };

        let blob;
        let filename;
        if (format === 'json') {
            blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
            filename = `${filenameBase}.json`;
        } else {
            const md = buildMarkdown(payload);
            blob = new Blob([md], { type: 'text/markdown' });
            filename = `${filenameBase}.md`;
        }

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function buildMarkdown(payload) {
        const fb = payload.feedback;
        let md = `# Lit Passage Practice — Export\n\n`;
        md += `**Exported:** ${payload.exported_at}\n\n`;
        md += `## Passage\n\n**${payload.title}** by ${payload.author}\n\n`;
        md += `Source: <${payload.source_url}>\n\n`;
        md += `> ${payload.passage.replace(/\n/g, '\n> ')}\n\n`;
        md += `*${payload.passage_word_count} words*\n\n`;
        md += `## Your Analysis\n\n${payload.response || '*(No response entered.)*'}\n\n`;
        md += `*${payload.response_word_count} words*\n\n`;
        if (fb) {
            md += `## Feedback\n\n**Rating:** ${fb.rating} (${fb.passed}/${fb.total})\n\n`;
            md += `### Checklist\n\n`;
            for (const key of Object.keys(fb.checks)) {
                const item = fb.checks[key];
                md += `- [${item.passed ? 'x' : ' '}] ${item.label}\n`;
            }
            md += `\n### Suggestions\n\n`;
            for (const s of fb.suggestions) {
                md += `- ${s}\n`;
            }
        }
        return md;
    }

    // Event listeners
    newPassageBtn.addEventListener('click', loadPassage);
    submitBtn.addEventListener('click', submitFeedback);
    exportBtn.addEventListener('click', exportResponse);

    responseInput.addEventListener('input', () => {
        responseWordCount.textContent = `${countWords(responseInput.value)} words`;
    });

    // Load an initial passage on startup
    loadPassage();
})();
