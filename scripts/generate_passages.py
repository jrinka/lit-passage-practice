#!/usr/bin/env python3
"""Pre-fetch curated passages from Project Gutenberg for offline fallback."""

import json
import random
import re
import time
from pathlib import Path

import requests

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

START_RE = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.IGNORECASE | re.DOTALL)
END_RE = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.IGNORECASE | re.DOTALL)


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def strip_gutenberg_boilerplate(text: str) -> str:
    start = START_RE.search(text)
    if start:
        text = text[start.end():]
    end = END_RE.search(text)
    if end:
        text = text[:end.start()]
    return text.strip()


def clean_paragraphs(text: str):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return [re.sub(r"\s+", " ", p) for p in paras]


def sentences_from_paragraph(p: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]


def extract_passage(text: str, min_words: int = 100, max_words: int = 200):
    body = strip_gutenberg_boilerplate(text)
    if not body:
        return None

    paragraphs = clean_paragraphs(body)
    candidates = []

    for p in paragraphs:
        wc = count_words(p)
        if min_words <= wc <= max_words:
            candidates.append(p)

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

    for p in paragraphs:
        if count_words(p) > max_words:
            sentences = sentences_from_paragraph(p)
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

    words = re.findall(r"\S+", body)
    if len(words) < min_words:
        return None
    max_start = len(words) - max_words - 1
    start = random.randint(0, max(0, max_start))
    window = words[start:start + max_words]
    joined = " ".join(window)
    last_sentence_end = max(joined.rfind(". "), joined.rfind("! "), joined.rfind("? "))
    if last_sentence_end > len(joined) // 2:
        joined = joined[: last_sentence_end + 1]
    if min_words <= count_words(joined) <= max_words:
        return joined
    return " ".join(window[:min(max_words, len(window))])


def fetch_book_text(book_id: int):
    urls = [
        f"https://www.gutenberg.org/ebooks/{book_id}.txt.utf-8",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
    ]
    for url in urls:
        try:
            resp = requests.get(url, headers={"User-Agent": "LitPassagePractice/1.0"}, timeout=10)
            resp.raise_for_status()
            if len(resp.text) < 500:
                continue
            return resp.text
        except Exception:
            continue
    return None


def main():
    random.seed(42)
    out_path = Path(__file__).parent.parent / "static" / "passages.json"

    # Resume from existing file if present.
    if out_path.exists():
        passages = json.loads(out_path.read_text(encoding="utf-8"))
        existing_titles = {p["title"] for p in passages}
        print(f"Resuming with {len(passages)} existing passages.")
    else:
        passages = []
        existing_titles = set()

    for book in BOOKS:
        if book["title"] in existing_titles:
            continue

        print(f"Fetching {book['title']}...", end=" ", flush=True)
        text = fetch_book_text(book["id"])
        if not text:
            print("failed")
            out_path.write_text(json.dumps(passages, indent=2), encoding="utf-8")
            continue

        passage = extract_passage(text)
        if not passage:
            print("no passage")
            out_path.write_text(json.dumps(passages, indent=2), encoding="utf-8")
            continue

        passages.append({
            "title": book["title"],
            "author": book["author"],
            "source_url": f"https://www.gutenberg.org/ebooks/{book['id']}",
            "passage": passage,
            "word_count": count_words(passage),
        })
        print(f"ok ({count_words(passage)} words)")
        out_path.write_text(json.dumps(passages, indent=2), encoding="utf-8")
        time.sleep(0.5)

    print(f"\nWrote {len(passages)} passages to {out_path}")


if __name__ == "__main__":
    main()
