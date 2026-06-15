# Static Client Conversion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the Flask-based Lit Passage Practice app into a static client-side app that runs by opening `passages.html` in a browser, with no Python server required.

**Architecture:** Move the book list, passage extraction, and feedback rubric from `app.py` into `static/app.js`. Add a `static/passages.json` fallback for when live Project Gutenberg fetches fail. Replace `index.html` with `passages.html` as the entry point. Remove the Python backend and update the README.

**Tech Stack:** Vanilla HTML, CSS, JavaScript (ES2020). No build tools, no frameworks.

---

## File structure

| File | Action | Responsibility |
|------|--------|----------------|
| `passages.html` | Create | Entry page (rename of `index.html`) |
| `static/style.css` | Keep | Existing styles |
| `static/app.js` | Replace | All client-side logic: data, fetch, extraction, feedback, export, UI wiring |
| `static/passages.json` | Create | Offline fallback passages |
| `index.html` | Delete | Replaced by `passages.html` |
| `app.py` | Delete | No longer needed |
| `requirements.txt` | Delete | No longer needed |
| `README.md` | Modify | Update setup/run instructions |

---

### Task 1: Create offline fallback passages

**Files:**
- Create: `static/passages.json`

- [ ] **Step 1: Write the fallback JSON file**

```json
[
  {
    "title": "Pride and Prejudice",
    "author": "Jane Austen",
    "passage": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered as the rightful property of some one or other of their daughters. \"My dear Mr. Bennet,\" said his lady to him one day, \"have you heard that Netherfield Park is let at last?\" Mr. Bennet replied that he had not. \"But it is,\" returned she; \"for Mrs. Long has just been here, and she told me all about it.\" Mr. Bennet made no answer. \"Do not you want to know who has taken it?\" cried his wife impatiently. \"You want to tell me, and I have no objection to hearing it.\" This was invitation enough."
  },
  {
    "title": "Moby-Dick",
    "author": "Herman Melville",
    "passage": "Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world. It is a way I have of driving off the spleen and regulating the circulation. Whenever I find myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever I find myself involuntarily pausing before coffin warehouses, and bringing up the rear of every funeral I meet; and especially whenever my hypos get such an upper hand of me, that it requires a strong moral principle to prevent me from deliberately stepping into the street, and methodically knocking people's hats off—then, I account it high time to get to sea as soon as I can."
  }
]
```

- [ ] **Step 2: Verify the JSON is valid**

Run:

```bash
cd "/Users/jrinka/Kimi Code Projects/Lit Passage Practice"
python3 -m json.tool static/passages.json > /dev/null && echo "valid"
```

Expected output:

```
valid
```

- [ ] **Step 3: Commit**

```bash
git add static/passages.json
git commit -m "feat: add offline fallback passages"
```

---

### Task 2: Rewrite the client-side JavaScript

**Files:**
- Replace: `static/app.js`

- [ ] **Step 1: Delete the old `static/app.js` content**

The new file will fully replace it.

- [ ] **Step 2: Write the new `static/app.js`**

```javascript
/**
 * Lit Passage Practice — static client-side app.
 *
 * Fetches public-domain classics from Project Gutenberg and runs a
 * lightweight rubric check on the user's analysis. Falls back to bundled
 * passages if live fetching fails.
 */

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------

const BOOKS = [
  { id: 1342, title: "Pride and Prejudice", author: "Jane Austen" },
  { id: 158, title: "Emma", author: "Jane Austen" },
  { id: 161, title: "Sense and Sensibility", author: "Jane Austen" },
  { id: 105, title: "Persuasion", author: "Jane Austen" },
  { id: 1260, title: "Jane Eyre", author: "Charlotte Brontë" },
  { id: 768, title: "Wuthering Heights", author: "Emily Brontë" },
  { id: 1400, title: "Great Expectations", author: "Charles Dickens" },
  { id: 98, title: "A Tale of Two Cities", author: "Charles Dickens" },
  { id: 46, title: "A Christmas Carol", author: "Charles Dickens" },
  { id: 2701, title: "Moby-Dick", author: "Herman Melville" },
  { id: 74, title: "The Adventures of Tom Sawyer", author: "Mark Twain" },
  { id: 76, title: "The Adventures of Huckleberry Finn", author: "Mark Twain" },
  { id: 11, title: "Alice's Adventures in Wonderland", author: "Lewis Carroll" },
  { id: 1524, title: "Hamlet", author: "William Shakespeare" },
  { id: 1533, title: "Macbeth", author: "William Shakespeare" },
  { id: 1513, title: "Romeo and Juliet", author: "William Shakespeare" },
  { id: 1514, title: "A Midsummer Night's Dream", author: "William Shakespeare" },
  { id: 844, title: "The Importance of Being Earnest", author: "Oscar Wilde" },
  { id: 174, title: "The Picture of Dorian Gray", author: "Oscar Wilde" },
  { id: 84, title: "Frankenstein", author: "Mary Shelley" },
  { id: 345, title: "Dracula", author: "Bram Stoker" },
  { id: 42, title: "The Strange Case of Dr Jekyll and Mr Hyde", author: "Robert Louis Stevenson" },
  { id: 120, title: "Treasure Island", author: "Robert Louis Stevenson" },
  { id: 219, title: "Heart of Darkness", author: "Joseph Conrad" },
  { id: 55, title: "The Wonderful Wizard of Oz", author: "L. Frank Baum" },
  { id: 521, title: "Robinson Crusoe", author: "Daniel Defoe" },
  { id: 829, title: "Gulliver's Travels", author: "Jonathan Swift" },
  { id: 33, title: "The Scarlet Letter", author: "Nathaniel Hawthorne" },
  { id: 209, title: "The Turn of the Screw", author: "Henry James" },
  { id: 160, title: "The Awakening", author: "Kate Chopin" },
  { id: 1952, title: "The Yellow Wallpaper", author: "Charlotte Perkins Gilman" },
  { id: 4517, title: "Ethan Frome", author: "Edith Wharton" },
  { id: 541, title: "The Age of Innocence", author: "Edith Wharton" },
  { id: 284, title: "The House of Mirth", author: "Edith Wharton" },
  { id: 2600, title: "War and Peace", author: "Leo Tolstoy" },
  { id: 1399, title: "Anna Karenina", author: "Leo Tolstoy" },
  { id: 2554, title: "Crime and Punishment", author: "Fyodor Dostoevsky" },
  { id: 28054, title: "The Brothers Karamazov", author: "Fyodor Dostoevsky" },
  { id: 135, title: "Les Misérables", author: "Victor Hugo" },
  { id: 1184, title: "The Count of Monte Cristo", author: "Alexandre Dumas" },
  { id: 1257, title: "The Three Musketeers", author: "Alexandre Dumas" },
  { id: 103, title: "Around the World in Eighty Days", author: "Jules Verne" },
  { id: 164, title: "Twenty Thousand Leagues under the Sea", author: "Jules Verne" },
  { id: 36, title: "The War of the Worlds", author: "H. G. Wells" },
  { id: 35, title: "The Time Machine", author: "H. G. Wells" },
  { id: 236, title: "The Jungle Book", author: "Rudyard Kipling" },
  { id: 215, title: "The Call of the Wild", author: "Jack London" },
  { id: 37106, title: "Little Women", author: "Louisa May Alcott" },
  { id: 17396, title: "The Secret Garden", author: "Frances Hodgson Burnett" },
  { id: 289, title: "The Wind in the Willows", author: "Kenneth Grahame" },
  { id: 16, title: "Peter Pan", author: "J. M. Barrie" },
  { id: 271, title: "Black Beauty", author: "Anna Sewell" },
  { id: 82, title: "Ivanhoe", author: "Walter Scott" },
  { id: 2765, title: "The Last of the Mohicans", author: "James Fenimore Cooper" },
  { id: 60, title: "The Scarlet Pimpernel", author: "Baroness Orczy" },
  { id: 1695, title: "The Man Who Was Thursday", author: "G. K. Chesterton" },
  { id: 2413, title: "Madame Bovary", author: "Gustave Flaubert" },
  { id: 1727, title: "The Odyssey", author: "Homer (Samuel Butler translation)" },
  { id: 6130, title: "The Iliad", author: "Homer (Samuel Butler translation)" },
  { id: 2383, title: "The Canterbury Tales", author: "Geoffrey Chaucer" },
  { id: 2000, title: "Don Quixote", author: "Miguel de Cervantes (Ormsby translation)" },
  { id: 15492, title: "A Doll's House", author: "Henrik Ibsen" },
  { id: 2500, title: "Siddhartha", author: "Hermann Hesse" },
];

let FALLBACK_PASSAGES = [];

// ---------------------------------------------------------------------------
// Text helpers
// ---------------------------------------------------------------------------

const START_RE = /\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*/is;
const END_RE = /\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*/is;

function countWords(text) {
  const matches = text.match(/\b\w+\b/g);
  return matches ? matches.length : 0;
}

function stripGutenbergBoilerplate(text) {
  const start = START_RE.exec(text);
  if (start) {
    text = text.slice(start.index + start[0].length);
  }
  const end = END_RE.exec(text);
  if (end) {
    text = text.slice(0, end.index);
  }
  return text.trim();
}

function cleanParagraphs(text) {
  return text
    .split(/\n\s*\n/)
    .map((p) => p.trim().replace(/\s+/g, " "))
    .filter((p) => p.length > 0);
}

function sentencesFromParagraph(p) {
  return p
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

function randomInt(max) {
  return Math.floor(Math.random() * max);
}

function sample(array) {
  return array[randomInt(array.length)];
}

function extractPassage(text, minWords = 100, maxWords = 200) {
  const body = stripGutenbergBoilerplate(text);
  if (!body) return null;

  const paragraphs = cleanParagraphs(body);
  const candidates = [];

  // 1. Whole paragraphs that already fit the range.
  for (const p of paragraphs) {
    const wc = countWords(p);
    if (minWords <= wc && wc <= maxWords) {
      candidates.push(p);
    }
  }

  // 2. Merge a few short consecutive paragraphs.
  for (let i = 0; i < paragraphs.length; i++) {
    const merged = [];
    let wc = 0;
    for (let j = i; j < Math.min(i + 6, paragraphs.length); j++) {
      merged.push(paragraphs[j]);
      wc += countWords(paragraphs[j]);
      if (minWords <= wc && wc <= maxWords) {
        candidates.push(merged.join(" "));
        break;
      } else if (wc > maxWords) {
        break;
      }
    }
  }

  // 3. Sentence-window from a paragraph that is too long.
  for (const p of paragraphs) {
    if (countWords(p) > maxWords) {
      const sentences = sentencesFromParagraph(p);
      for (let start = 0; start < sentences.length; start++) {
        const chunk = [];
        let wc = 0;
        for (const s of sentences.slice(start)) {
          chunk.push(s);
          wc += countWords(s);
          if (minWords <= wc && wc <= maxWords) {
            candidates.push(chunk.join(" "));
            break;
          } else if (wc > maxWords) {
            break;
          }
        }
      }
    }
  }

  if (candidates.length > 0) {
    return sample(candidates);
  }

  // Final fallback: grab a random word window and trim to a sentence end.
  const words = body.match(/\S+/g) || [];
  if (words.length < minWords) return null;

  const maxStart = Math.max(0, words.length - maxWords - 1);
  const start = randomInt(maxStart + 1);
  const window = words.slice(start, start + maxWords);
  let joined = window.join(" ");

  const ends = [". ", "! ", "? "]
    .map((mark) => joined.lastIndexOf(mark))
    .filter((idx) => idx !== -1);
  const lastSentenceEnd = ends.length ? Math.max(...ends) : -1;

  if (lastSentenceEnd > joined.length / 2) {
    joined = joined.slice(0, lastSentenceEnd + 1);
  }

  const finalWc = countWords(joined);
  if (minWords <= finalWc && finalWc <= maxWords) {
    return joined;
  }
  return window.slice(0, Math.min(maxWords, window.length)).join(" ");
}

// ---------------------------------------------------------------------------
// Fetching
// ---------------------------------------------------------------------------

const TEXT_CACHE = {};

async function fetchBookText(bookId) {
  if (TEXT_CACHE[bookId] !== undefined) {
    return TEXT_CACHE[bookId];
  }

  const urls = [
    `https://www.gutenberg.org/ebooks/${bookId}.txt.utf-8`,
    `https://www.gutenberg.org/files/${bookId}/${bookId}-0.txt`,
  ];

  for (const url of urls) {
    try {
      const resp = await fetch(url, { headers: { "User-Agent": "LitPassagePractice/1.0" } });
      if (!resp.ok) continue;
      const text = await resp.text();
      if (text.length < 500) continue;
      TEXT_CACHE[bookId] = text;
      return text;
    } catch (err) {
      // Try next URL or fall through.
    }
  }

  TEXT_CACHE[bookId] = null;
  return null;
}

async function loadFallbackPassages() {
  if (FALLBACK_PASSAGES.length > 0) return;
  try {
    const resp = await fetch("static/passages.json");
    if (resp.ok) {
      FALLBACK_PASSAGES = await resp.json();
    }
  } catch (err) {
    console.error("Failed to load fallback passages", err);
    FALLBACK_PASSAGES = [];
  }
}

async function getRandomPassage() {
  await loadFallbackPassages();

  for (let attempt = 0; attempt < 10; attempt++) {
    const book = sample(BOOKS);
    const text = await fetchBookText(book.id);
    if (!text) continue;

    const passage = extractPassage(text);
    if (passage) {
      return {
        id: book.id,
        title: book.title,
        author: book.author,
        source_url: `https://www.gutenberg.org/ebooks/${book.id}`,
        passage,
        word_count: countWords(passage),
        fallback: false,
      };
    }
  }

  // Fallback
  if (FALLBACK_PASSAGES.length === 0) {
    return null;
  }
  const fb = sample(FALLBACK_PASSAGES);
  return {
    id: null,
    title: fb.title,
    author: fb.author,
    source_url: "https://www.gutenberg.org/",
    passage: fb.passage,
    word_count: countWords(fb.passage),
    fallback: true,
  };
}

// ---------------------------------------------------------------------------
// Feedback
// ---------------------------------------------------------------------------

function evaluateFeedback(passage, response) {
  const responseLower = response.toLowerCase();
  const wc = countWords(response);

  const checks = {
    length: {
      label: "Response is at least 50 words",
      passed: wc >= 50,
    },
    text_reference: {
      label: "Refers to specific evidence from the passage",
      passed: /["']|\b(?:line|passage|text|says|describes|shows|suggests|quotes|writes|states)\b/.test(responseLower),
    },
    device_or_theme: {
      label: "Mentions a literary device, tone, or theme",
      passed: /\b(?:metaphor|simile|imagery|symbol|theme|tone|irony|personification|foreshadowing|conflict|mood|diction|syntax|character|setting|narrator|perspective|point of view|alliteration)\b/.test(responseLower),
    },
    explanation: {
      label: "Explains how the evidence supports an interpretation",
      passed: /\b(?:because|shows|suggests|indicates|demonstrates|reveals|implies|creates|emphasizes|highlights|conveys|illustrates|represents|reflects|therefore|thus)\b/.test(responseLower),
    },
  };

  const passed = Object.values(checks).filter((c) => c.passed).length;
  const total = Object.keys(checks).length;

  let rating;
  if (passed === total) rating = "Strong";
  else if (passed >= total / 2) rating = "Good";
  else rating = "Developing";

  const missing = Object.values(checks)
    .filter((c) => !c.passed)
    .map((c) => c.label);

  const suggestions = [];
  if (!checks.length.passed) {
    suggestions.push("Try writing a bit more—aim for at least 50 words so you can develop your ideas.");
  }
  if (!checks.text_reference.passed) {
    suggestions.push("Quote or paraphrase a specific line from the passage to ground your analysis.");
  }
  if (!checks.device_or_theme.passed) {
    suggestions.push("Identify a literary device, tone, or theme the author is using.");
  }
  if (!checks.explanation.passed) {
    suggestions.push("Explain why the evidence matters—what does it show about meaning or effect?");
  }
  if (suggestions.length === 0) {
    suggestions.push("Great job! Your analysis covers the key elements of a strong response.");
  }

  return {
    response_word_count: wc,
    checks,
    passed,
    total,
    rating,
    missing,
    suggestions,
    generated_at: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// UI helpers
// ---------------------------------------------------------------------------

const els = {
  passageTitle: document.getElementById("passage-title"),
  passageBox: document.getElementById("passage-box"),
  passageAuthor: document.getElementById("passage-author"),
  passageWordCount: document.getElementById("passage-word-count"),
  sourceLink: document.getElementById("source-link"),
  newPassageBtn: document.getElementById("new-passage-btn"),
  responseInput: document.getElementById("response-input"),
  responseWordCount: document.getElementById("response-word-count"),
  submitBtn: document.getElementById("submit-btn"),
  exportBtn: document.getElementById("export-btn"),
  exportFormat: document.getElementById("export-format"),
  feedbackCard: document.getElementById("feedback-card"),
  scoreValue: document.getElementById("score-value"),
  rating: document.getElementById("rating"),
  checklist: document.getElementById("checklist"),
  suggestions: document.getElementById("suggestions"),
};

let currentPassage = null;
let currentFeedback = null;

function setLoading(isLoading) {
  els.newPassageBtn.disabled = isLoading;
  if (isLoading) {
    els.passageBox.innerHTML = '<div class="shimmer" id="passage-shimmer"><span></span><span></span><span></span></div>';
  }
}

function renderPassage(data) {
  if (!data) {
    els.passageTitle.textContent = "Couldn't load a passage";
    els.passageBox.textContent = "Please check your internet connection and try again.";
    els.passageAuthor.textContent = "—";
    els.passageWordCount.textContent = "— words";
    els.sourceLink.href = "#";
    currentPassage = null;
    return;
  }

  currentPassage = data;
  els.passageTitle.textContent = data.title;
  els.passageBox.textContent = data.passage;
  els.passageAuthor.textContent = data.author;
  els.passageWordCount.textContent = `${data.word_count} words`;
  els.sourceLink.href = data.source_url;
}

function renderFeedback(result) {
  currentFeedback = result;
  els.feedbackCard.classList.remove("hidden");
  els.scoreValue.textContent = `${result.passed}/${result.total}`;
  els.rating.textContent = result.rating;

  els.checklist.innerHTML = "";
  for (const check of Object.values(result.checks)) {
    const li = document.createElement("li");
    li.className = check.passed ? "check-pass" : "check-fail";
    li.textContent = `${check.passed ? "✓" : "✗"} ${check.label}`;
    els.checklist.appendChild(li);
  }

  const ul = els.suggestions.querySelector("ul");
  ul.innerHTML = "";
  for (const suggestion of result.suggestions) {
    const li = document.createElement("li");
    li.textContent = suggestion;
    ul.appendChild(li);
  }
}

// ---------------------------------------------------------------------------
// Export
// ---------------------------------------------------------------------------

function downloadBlob(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function exportMarkdown() {
  if (!currentPassage || !currentFeedback) return;
  const lines = [
    `# ${currentPassage.title}`,
    "",
    `**Author:** ${currentPassage.author}`,
    `**Source:** ${currentPassage.source_url}`,
    `**Word count:** ${currentPassage.word_count}`,
    "",
    "> " + currentPassage.passage.replace(/\n/g, "\n> "),
    "",
    "## Analysis",
    "",
    els.responseInput.value,
    "",
    "## Feedback",
    "",
    `**Rating:** ${currentFeedback.rating} (${currentFeedback.passed}/${currentFeedback.total})`,
    "",
    "### Checks",
    "",
    ...Object.values(currentFeedback.checks).map((c) => `- [${c.passed ? "x" : " "}] ${c.label}`),
    "",
    "### Suggestions",
    "",
    ...currentFeedback.suggestions.map((s) => `- ${s}`),
    "",
    `_Exported at ${currentFeedback.generated_at}_`,
  ];
  downloadBlob(`${currentPassage.title.replace(/\s+/g, "_")}_analysis.md`, lines.join("\n"), "text/markdown");
}

function exportJson() {
  if (!currentPassage || !currentFeedback) return;
  const payload = {
    passage: currentPassage,
    response: els.responseInput.value,
    feedback: currentFeedback,
  };
  downloadBlob(`${currentPassage.title.replace(/\s+/g, "_")}_analysis.json`, JSON.stringify(payload, null, 2), "application/json");
}

// ---------------------------------------------------------------------------
// Event wiring
// ---------------------------------------------------------------------------

async function loadNewPassage() {
  setLoading(true);
  els.feedbackCard.classList.add("hidden");
  els.responseInput.value = "";
  els.responseWordCount.textContent = "0 words";
  currentFeedback = null;
  const data = await getRandomPassage();
  renderPassage(data);
  setLoading(false);
}

function handleSubmit() {
  if (!currentPassage) return;
  const response = els.responseInput.value.trim();
  if (!response) {
    alert("Write a short analysis before submitting.");
    return;
  }
  const result = evaluateFeedback(currentPassage.passage, response);
  renderFeedback(result);
}

function handleExport() {
  const format = els.exportFormat.value;
  if (format === "markdown") {
    exportMarkdown();
  } else {
    exportJson();
  }
}

function init() {
  els.newPassageBtn.addEventListener("click", loadNewPassage);
  els.submitBtn.addEventListener("click", handleSubmit);
  els.exportBtn.addEventListener("click", handleExport);

  els.responseInput.addEventListener("input", () => {
    const wc = countWords(els.responseInput.value);
    els.responseWordCount.textContent = `${wc} word${wc === 1 ? "" : "s"}`;
  });

  loadNewPassage();
}

init();
```

- [ ] **Step 3: Validate JavaScript syntax**

Run:

```bash
cd "/Users/jrinka/Kimi Code Projects/Lit Passage Practice"
node --check static/app.js && echo "syntax ok"
```

Expected output:

```
syntax ok
```

- [ ] **Step 4: Commit**

```bash
git add static/app.js
git commit -m "feat: convert backend logic to client-side JavaScript"
```

---

### Task 3: Create the new entry page

**Files:**
- Create: `passages.html`
- Delete: `index.html`

- [ ] **Step 1: Copy `index.html` to `passages.html`**

Run:

```bash
cd "/Users/jrinka/Kimi Code Projects/Lit Passage Practice"
cp index.html passages.html
```

- [ ] **Step 2: Change resource paths from absolute to relative**

Because the page will be opened directly from the filesystem, absolute paths like `/static/style.css` will not resolve. Edit `passages.html` so the resource links use relative paths:

```html
<link rel="stylesheet" href="static/style.css">
<script src="static/app.js"></script>
```

- [ ] **Step 3: Delete `index.html`**

Run:

```bash
rm index.html
```

- [ ] **Step 4: Commit**

```bash
git add passages.html
git rm index.html
git commit -m "feat: rename entry page from index.html to passages.html"
```

---

### Task 4: Remove Python backend and update docs

**Files:**
- Delete: `app.py`
- Delete: `requirements.txt`
- Modify: `README.md`

- [ ] **Step 1: Delete the backend files**

Run:

```bash
cd "/Users/jrinka/Kimi Code Projects/Lit Passage Practice"
rm app.py requirements.txt
```

- [ ] **Step 2: Rewrite `README.md`**

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git rm app.py requirements.txt
git add README.md
git commit -m "chore: remove Flask backend and update README for static usage"
```

---

## Manual testing checklist

After all tasks are complete, open `passages.html` in Chrome, Firefox, and Safari and verify:

1. A passage loads on page open.
2. Clicking **New Passage** loads a different passage.
3. Writing fewer than 50 words and clicking **Submit for Feedback** shows “Developing” and suggests writing more.
4. Writing 50+ words without evidence reference shows a suggestion to quote the passage.
5. Writing a strong analysis returns “Strong.”
6. **Export** → Markdown downloads a `.md` file containing the passage, analysis, and feedback.
7. **Export** → JSON downloads a `.json` file with the same data.
8. Disconnect from the internet and reload; the app still shows a passage from the fallback JSON.

---

## Self-review

- **Spec coverage:** All sections of the design spec are addressed: static conversion, `passages.html`, fallback JSON, client-side extraction/feedback/export, README update, backend removal.
- **Placeholder scan:** No TBD/TODO/vague steps. Every step includes exact file paths, commands, or code.
- **Type consistency:** DOM element IDs match those in `index.html`/`passages.html`. Function names are consistent throughout the new `app.js`.
