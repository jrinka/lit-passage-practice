#!/usr/bin/env python3
"""Lit Passage Practice — Flask backend that proxies and excerpts Project Gutenberg classics."""

import random
import re
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

# ---------------------------------------------------------------------------
# Curated list of classic Project Gutenberg ebooks (novels, plays, stories)
# ---------------------------------------------------------------------------
BOOKS = [
    {"id": 1342, "title": "Pride and Prejudice", "author": "Jane Austen"},
    {"id": 158, "title": "Emma", "author": "Jane Austen"},
    {"id": 161, "title": "Sense and Sensibility", "author": "Jane Austen"},
    {"id": 105, "title": "Persuasion", "author": "Jane Austen"},
    {"id": 1260, "title": "Jane Eyre", "author": "Charlotte Brontë"},
    {"id": 768, "title": "Wuthering Heights", "author": "Emily Brontë"},
    {"id": 1400, "title": "Great Expectations", "author": "Charles Dickens"},
    {"id": 98, "title": "A Tale of Two Cities", "author": "Charles Dickens"},
    {"id": 46, "title": "A Christmas Carol", "author": "Charles Dickens"},
    {"id": 2701, "title": "Moby-Dick", "author": "Herman Melville"},
    {"id": 74, "title": "The Adventures of Tom Sawyer", "author": "Mark Twain"},
    {"id": 76, "title": "The Adventures of Huckleberry Finn", "author": "Mark Twain"},
    {"id": 11, "title": "Alice's Adventures in Wonderland", "author": "Lewis Carroll"},
    {"id": 1524, "title": "Hamlet", "author": "William Shakespeare"},
    {"id": 1533, "title": "Macbeth", "author": "William Shakespeare"},
    {"id": 1513, "title": "Romeo and Juliet", "author": "William Shakespeare"},
    {"id": 1514, "title": "A Midsummer Night's Dream", "author": "William Shakespeare"},
    {"id": 844, "title": "The Importance of Being Earnest", "author": "Oscar Wilde"},
    {"id": 174, "title": "The Picture of Dorian Gray", "author": "Oscar Wilde"},
    {"id": 84, "title": "Frankenstein", "author": "Mary Shelley"},
    {"id": 345, "title": "Dracula", "author": "Bram Stoker"},
    {"id": 42, "title": "The Strange Case of Dr Jekyll and Mr Hyde", "author": "Robert Louis Stevenson"},
    {"id": 120, "title": "Treasure Island", "author": "Robert Louis Stevenson"},
    {"id": 219, "title": "Heart of Darkness", "author": "Joseph Conrad"},
    {"id": 55, "title": "The Wonderful Wizard of Oz", "author": "L. Frank Baum"},
    {"id": 521, "title": "Robinson Crusoe", "author": "Daniel Defoe"},
    {"id": 829, "title": "Gulliver's Travels", "author": "Jonathan Swift"},
    {"id": 33, "title": "The Scarlet Letter", "author": "Nathaniel Hawthorne"},
    {"id": 209, "title": "The Turn of the Screw", "author": "Henry James"},
    {"id": 160, "title": "The Awakening", "author": "Kate Chopin"},
    {"id": 1952, "title": "The Yellow Wallpaper", "author": "Charlotte Perkins Gilman"},
    {"id": 4517, "title": "Ethan Frome", "author": "Edith Wharton"},
    {"id": 541, "title": "The Age of Innocence", "author": "Edith Wharton"},
    {"id": 284, "title": "The House of Mirth", "author": "Edith Wharton"},
    {"id": 2600, "title": "War and Peace", "author": "Leo Tolstoy"},
    {"id": 1399, "title": "Anna Karenina", "author": "Leo Tolstoy"},
    {"id": 2554, "title": "Crime and Punishment", "author": "Fyodor Dostoevsky"},
    {"id": 28054, "title": "The Brothers Karamazov", "author": "Fyodor Dostoevsky"},
    {"id": 135, "title": "Les Misérables", "author": "Victor Hugo"},
    {"id": 1184, "title": "The Count of Monte Cristo", "author": "Alexandre Dumas"},
    {"id": 1257, "title": "The Three Musketeers", "author": "Alexandre Dumas"},
    {"id": 103, "title": "Around the World in Eighty Days", "author": "Jules Verne"},
    {"id": 164, "title": "Twenty Thousand Leagues under the Sea", "author": "Jules Verne"},
    {"id": 36, "title": "The War of the Worlds", "author": "H. G. Wells"},
    {"id": 35, "title": "The Time Machine", "author": "H. G. Wells"},
    {"id": 236, "title": "The Jungle Book", "author": "Rudyard Kipling"},
    {"id": 215, "title": "The Call of the Wild", "author": "Jack London"},
    {"id": 37106, "title": "Little Women", "author": "Louisa May Alcott"},
    {"id": 17396, "title": "The Secret Garden", "author": "Frances Hodgson Burnett"},
    {"id": 289, "title": "The Wind in the Willows", "author": "Kenneth Grahame"},
    {"id": 16, "title": "Peter Pan", "author": "J. M. Barrie"},
    {"id": 271, "title": "Black Beauty", "author": "Anna Sewell"},
    {"id": 82, "title": "Ivanhoe", "author": "Walter Scott"},
    {"id": 2765, "title": "The Last of the Mohicans", "author": "James Fenimore Cooper"},
    {"id": 60, "title": "The Scarlet Pimpernel", "author": "Baroness Orczy"},
    {"id": 1695, "title": "The Man Who Was Thursday", "author": "G. K. Chesterton"},
    {"id": 2413, "title": "Madame Bovary", "author": "Gustave Flaubert"},
    {"id": 1727, "title": "The Odyssey", "author": "Homer (Samuel Butler translation)"},
    {"id": 6130, "title": "The Iliad", "author": "Homer (Samuel Butler translation)"},
    {"id": 2383, "title": "The Canterbury Tales", "author": "Geoffrey Chaucer"},
    {"id": 2000, "title": "Don Quixote", "author": "Miguel de Cervantes (Ormsby translation)"},
    {"id": 15492, "title": "A Doll's House", "author": "Henrik Ibsen"},
    {"id": 2500, "title": "Siddhartha", "author": "Hermann Hesse"},
]

# A small offline fallback so the app still works if Gutenberg is unreachable.
FALLBACK_PASSAGES = [
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "passage": (
            "It is a truth universally acknowledged, that a single man in possession of a good fortune, "
            "must be in want of a wife. However little known the feelings or views of such a man may be on his "
            "first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, "
            "that he is considered as the rightful property of some one or other of their daughters. "
            "\"My dear Mr. Bennet,\" said his lady to him one day, \"have you heard that Netherfield Park is let at last?\" "
            "Mr. Bennet replied that he had not. \"But it is,\" returned she; \"for Mrs. Long has just been here, and she "
            "told me all about it.\" Mr. Bennet made no answer. \"Do not you want to know who has taken it?\" cried his "
            "wife impatiently. \"You want to tell me, and I have no objection to hearing it.\" This was invitation enough."
        ),
    },
    {
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "passage": (
            "Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, "
            "and nothing particular to interest me on shore, I thought I would sail about a little and see the watery "
            "part of the world. It is a way I have of driving off the spleen and regulating the circulation. Whenever "
            "I find myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever "
            "I find myself involuntarily pausing before coffin warehouses, and bringing up the rear of every funeral I "
            "meet; and especially whenever my hypos get such an upper hand of me, that it requires a strong moral "
            "principle to prevent me from deliberately stepping into the street, and methodically knocking people's hats "
            "off—then, I account it high time to get to sea as soon as I can."
        ),
    },
]

TEXT_CACHE = {}

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

START_RE = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.IGNORECASE | re.DOTALL)
END_RE = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.IGNORECASE | re.DOTALL)


def count_words(text: str) -> int:
    """Approximate word count using simple regex word boundaries."""
    return len(re.findall(r"\b\w+\b", text))


def strip_gutenberg_boilerplate(text: str) -> str:
    """Remove the standard Project Gutenberg header and footer."""
    start = START_RE.search(text)
    if start:
        text = text[start.end():]
    end = END_RE.search(text)
    if end:
        text = text[:end.start()]
    return text.strip()


def clean_paragraphs(text: str):
    """Split text into cleaned paragraphs."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return [re.sub(r"\s+", " ", p) for p in paras]


def _sentences_from_paragraph(p: str):
    """Split a paragraph into sentences without destroying punctuation."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]


def extract_passage(text: str, min_words: int = 100, max_words: int = 200):
    """Return a contiguous 100–200 word passage extracted from a Gutenberg text."""
    body = strip_gutenberg_boilerplate(text)
    if not body:
        return None

    paragraphs = clean_paragraphs(body)
    candidates = []

    # 1. Whole paragraphs that already fit the range.
    for p in paragraphs:
        wc = count_words(p)
        if min_words <= wc <= max_words:
            candidates.append(p)

    # 2. Merge a few short consecutive paragraphs.
    for i in range(len(paragraphs)):
        merged = []
        wc = 0
        for j in range(i, min(i + 6, len(paragraphs))):
            merged.append(paragraphs[j])
            wc += count_words(paragraphs[j])
            if min_words <= wc <= max_words:
                candidates.append(" ".join(merged))
                break
            elif wc > max_words:
                break

    # 3. Sentence-window from a paragraph that is too long.
    for p in paragraphs:
        if count_words(p) > max_words:
            sentences = _sentences_from_paragraph(p)
            for start in range(len(sentences)):
                chunk = []
                wc = 0
                for s in sentences[start:]:
                    chunk.append(s)
                    wc += count_words(s)
                    if min_words <= wc <= max_words:
                        candidates.append(" ".join(chunk))
                        break
                    elif wc > max_words:
                        break

    if candidates:
        return random.choice(candidates)

    # Final fallback: grab a random word window and trim to a sentence end.
    words = re.findall(r"\S+", body)
    if len(words) < min_words:
        return None
    max_start = len(words) - max_words - 1
    start = random.randint(0, max(0, max_start))
    window = words[start:start + max_words]
    joined = " ".join(window)
    # Try to end at a sentence boundary.
    last_sentence_end = max(joined.rfind(". "), joined.rfind("! "), joined.rfind("? "))
    if last_sentence_end > len(joined) // 2:
        joined = joined[: last_sentence_end + 1]
    if min_words <= count_words(joined) <= max_words:
        return joined
    return " ".join(window[:min(max_words, len(window))])


# ---------------------------------------------------------------------------
# Gutenberg fetching
# ---------------------------------------------------------------------------

HEADERS = {"User-Agent": "LitPassagePractice/1.0 (educational exercise)"}


def fetch_book_text(book_id: int):
    """Fetch plain text for a Gutenberg ebook, trying common URLs."""
    urls = [
        f"https://www.gutenberg.org/ebooks/{book_id}.txt.utf-8",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
    ]
    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            if len(resp.text) < 500:
                continue
            return resp.text
        except Exception:
            continue
    return None


def get_random_passage():
    """Try several random books until a valid passage is produced."""
    for _ in range(10):
        book = random.choice(BOOKS)
        if book["id"] not in TEXT_CACHE:
            TEXT_CACHE[book["id"]] = fetch_book_text(book["id"])
        text = TEXT_CACHE.get(book["id"])
        if not text:
            continue
        passage = extract_passage(text)
        if passage:
            return {
                "id": book["id"],
                "title": book["title"],
                "author": book["author"],
                "source_url": f"https://www.gutenberg.org/ebooks/{book['id']}",
                "passage": passage,
                "word_count": count_words(passage),
            }
    # Fallback
    fb = random.choice(FALLBACK_PASSAGES)
    return {
        "id": None,
        "title": fb["title"],
        "author": fb["author"],
        "source_url": "https://www.gutenberg.org/",
        "passage": fb["passage"],
        "word_count": count_words(fb["passage"]),
        "fallback": True,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/random-passage")
def random_passage():
    return jsonify(get_random_passage())


@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.get_json(silent=True) or {}
    passage = data.get("passage", "")
    response = data.get("response", "")
    response_lower = response.lower()
    wc = count_words(response)

    checks = {
        "length": {
            "label": "Response is at least 50 words",
            "passed": wc >= 50,
        },
        "text_reference": {
            "label": "Refers to specific evidence from the passage",
            "passed": bool(re.search(
                r'["\']|\b(?:line|passage|text|says|describes|shows|suggests|quotes|writes|states)\b',
                response_lower,
            )),
        },
        "device_or_theme": {
            "label": "Mentions a literary device, tone, or theme",
            "passed": bool(re.search(
                r'\b(?:metaphor|simile|imagery|symbol|theme|tone|irony|personification|foreshadowing|'
                r'conflict|mood|diction|syntax|character|setting|narrator|perspective|point of view|alliteration)\b',
                response_lower,
            )),
        },
        "explanation": {
            "label": "Explains how the evidence supports an interpretation",
            "passed": bool(re.search(
                r'\b(?:because|shows|suggests|indicates|demonstrates|reveals|implies|creates|emphasizes|'
                r'highlights|conveys|illustrates|represents|reflects|therefore|thus)\b',
                response_lower,
            )),
        },
    }

    passed = sum(1 for c in checks.values() if c["passed"])
    total = len(checks)
    if passed == total:
        rating = "Strong"
    elif passed >= total // 2:
        rating = "Good"
    else:
        rating = "Developing"

    missing = [c["label"] for c in checks.values() if not c["passed"]]
    suggestions = []
    if "length" in [k for k, v in checks.items() if not v["passed"]]:
        suggestions.append("Try writing a bit more—aim for at least 50 words so you can develop your ideas.")
    if "text_reference" in [k for k, v in checks.items() if not v["passed"]]:
        suggestions.append("Quote or paraphrase a specific line from the passage to ground your analysis.")
    if "device_or_theme" in [k for k, v in checks.items() if not v["passed"]]:
        suggestions.append("Identify a literary device, tone, or theme the author is using.")
    if "explanation" in [k for k, v in checks.items() if not v["passed"]]:
        suggestions.append("Explain why the evidence matters—what does it show about meaning or effect?")
    if not suggestions:
        suggestions.append("Great job! Your analysis covers the key elements of a strong response.")

    return jsonify({
        "response_word_count": wc,
        "checks": checks,
        "passed": passed,
        "total": total,
        "rating": rating,
        "missing": missing,
        "suggestions": suggestions,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="127.0.0.1", port=port, debug=True)
