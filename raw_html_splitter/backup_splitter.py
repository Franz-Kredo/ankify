#!/Applications/MAMP/htdocs/venv/bin/python
"""
Script to split quiz HTML files into individual question files.

1. Ensures directories `./raw_quiz_html/` and `./split_quiz_html/` exist.
2. Reads all `.html`, `.htm`, or `.txt` files in `./raw_quiz_html/`.
3. Parses each file, extracting every `<div role="region" aria-label="Question" class="quiz_sortable question_holder ">` element.
4. Writes each extracted question div to `./split_quiz_html/{original_filename_stem}-{index}.txt`.

Requires:
    beautifulsoup4 (install via `pip install beautifulsoup4`)
"""
import os
import sys
from bs4 import BeautifulSoup

RAW_DIR = os.path.join('.', 'raw_quiz_html')
SPLIT_DIR = os.path.join('.', 'split_quiz_html')


def ensure_directories():
    """Create raw and split directories if they don't exist."""
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(SPLIT_DIR, exist_ok=True)


def split_html_file(input_path):
    """Parse and split one HTML file into individual question HTML snippets."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    # Select divs that mark questions
    question_divs = soup.select(
        'div.quiz_sortable.question_holder[role="region"][aria-label="Question"]'
    )
    if not question_divs:
        print(f"No question divs found in {input_path}")
        return

    basename = os.path.splitext(os.path.basename(input_path))[0]
    for idx, div in enumerate(question_divs, start=1):
        out_filename = f"{basename}-{idx}.txt"
        out_path = os.path.join(SPLIT_DIR, out_filename)
        with open(out_path, 'w', encoding='utf-8') as out_f:
            out_f.write(str(div))
        print(f"Wrote {out_path}")


def main():
    ensure_directories()

    for fname in os.listdir(RAW_DIR):
        if not fname.lower().endswith(('.html', '.htm', '.txt')):
            continue
        input_path = os.path.join(RAW_DIR, fname)
        if os.path.isfile(input_path):
            print(f"Processing {input_path}...")
            split_html_file(input_path)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
