# Lit Passage Practice

A small browser app for students to practice analyzing short extracts from public-domain classics on Project Gutenberg.

## What it does

- Loads a random 100–200 word extract from a curated list of classic books, plays, and stories.
- Displays the passage with title, author, word count, and a link to the source.
- Gives you a text box to write your analysis.
- **Submit for Feedback** runs a lightweight rubric check on your response.
- **Export Response** saves the passage, your analysis, and the feedback as JSON or Markdown.

## Run

Open `passages.html` in any modern web browser.

No installation or server is required.

## Files

- `passages.html` — App layout.
- `static/style.css` — App styling.
- `static/app.js` — Frontend logic.
- `static/passages.json` — Offline fallback passages.

## Notes

- The app tries to fetch texts live from Project Gutenberg. If Gutenberg is unreachable or blocks the request, it falls back to the bundled passages in `static/passages.json`.
- Feedback is rule-based (word count, evidence reference, literary device/theme mention, explanation). It does not use an external LLM.
