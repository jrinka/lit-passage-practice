# Lit Passage Practice

A small browser app for students to practice analyzing short extracts from public-domain classics on Project Gutenberg.

## What it does

- Loads a random 100–200 word extract from a curated list of classic books, plays, and stories.
- Displays the passage with title, author, word count, and a link to the source.
- Gives you a text box to write your analysis.
- **Submit for Feedback** runs a lightweight rubric check on your response.
- **Export Response** saves the passage, your analysis, and the feedback as JSON or Markdown.

## Setup

```bash
cd "Lit Passage Practice"
pip install -r requirements.txt
```

## Run

```bash
python3 app.py
```

Then open <http://127.0.0.1:5050> in your browser.

## Files

- `app.py` — Flask backend that proxies and excerpts Project Gutenberg texts.
- `static/index.html` — App layout.
- `static/style.css` — App styling.
- `static/app.js` — Frontend logic.
- `requirements.txt` — Python dependencies.

## Notes

- The app fetches texts live from Project Gutenberg. If Gutenberg is unreachable, it falls back to a small set of built-in passages.
- Feedback is rule-based (word count, evidence reference, literary device/theme mention, explanation). It does not use an external LLM.
