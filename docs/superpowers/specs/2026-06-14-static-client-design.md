# Lit Passage Practice — Static Client Design

## Goal
Make the project shareable and usable without asking recipients to install Python or run a server. The recipient should only need to open a file in a browser.

## Constraints
- No Python runtime required.
- No terminal commands required.
- Internet connection is acceptable for fetching live passages.
- Page entry file should be named `passages.html` rather than `index.html`.

## Chosen approach
Convert the Flask backend to client-side JavaScript and serve the app as static files. Keep the existing HTML structure and CSS styling.

## Architecture

### Files
- `passages.html` — renamed entry page (formerly `index.html`). Same layout, loads scripts at the bottom.
- `static/style.css` — unchanged styling.
- `static/app.js` — now contains:
  - Curated `BOOKS` list (ported from `app.py`).
  - Gutenberg text fetcher using the browser `fetch` API.
  - Boilerplate stripper, paragraph cleaner, and 100–200 word passage extractor (ported from Python regex).
  - Feedback rubric and scoring (ported from Python).
  - Export functionality using client-side blob downloads.
- `static/passages.json` — bundled fallback passages used when live fetching fails (CORS/network/offline).

### Removed files
- `app.py`
- `requirements.txt`

## Data flow
1. User opens `passages.html` in a browser.
2. On load (and on “New Passage”), the app selects a random book from `BOOKS`.
3. It attempts to fetch the plain text from Project Gutenberg over HTTPS.
4. If the fetch succeeds, the text is cleaned and a 100–200 word passage is extracted.
5. If the fetch fails (e.g., CORS blocked or offline), the app picks a passage from `static/passages.json`.
6. The user writes an analysis and clicks “Submit for Feedback.”
7. The four-check rubric runs in JavaScript and renders the feedback card.
8. “Export” saves the passage, analysis, and feedback as Markdown or JSON via a generated blob URL.

## Error handling
- Network/CORS failure → silently fall back to `static/passages.json`.
- Extraction failure → select another random book or fallback passage.
- Empty analysis on submit → show an inline message asking the user to write something first.
- Export failure → log to console and alert the user.

## Browser compatibility target
Modern evergreen browsers: Chrome, Firefox, Safari, Edge. ES2020 features are acceptable.

## Testing plan
1. Open `passages.html` directly in Chrome, Firefox, and Safari.
2. Click “New Passage” repeatedly; confirm passages render from both live and fallback sources.
3. Submit analyses that trigger each rubric failure mode (too short, no evidence, no device/theme, no explanation) and confirm appropriate suggestions appear.
4. Submit a strong analysis and confirm a “Strong” rating.
5. Test Markdown and JSON export downloads contain the expected fields.
6. Verify the page title and heading still read “Lit Passage Practice” (only the filename changes).

## Open questions / notes
- Project Gutenberg does not send CORS headers, so direct browser fetches may fail in many environments. The fallback JSON file ensures the app remains usable.
- If offline-first behavior becomes important later, `passages.json` can be expanded with more curated extracts.
