#!/usr/bin/env python3
"""
Script to split quiz HTML files into individual question files and adjust answer elements:

1. Ensures directories `./raw_quiz_html/` and `./split_quiz_html/` exist.
2. Reads all `.html`, `.htm`, or `.txt` files in `./raw_quiz_html/`.
3. Parses each file, extracting every `<div role="region" aria-label="Question" class="quiz_sortable question_holder">` element.
4. Within each question:
   - Remove any `<span class="answer_arrow incorrect">…</span>` entirely.
   - Replace any `class="correct"` token with `info`, and change text `Correct!` to `Correct answer`.
   - Remove `wrong_answer` and `selected_answer` classes, and uncheck any child radio/checkbox inputs.
   - For each updated `info` span, add the `checked` attribute to its associated input (matched via `aria-describedby`).
5. Writes each modified question div to `./split_quiz_html/{original_name}-{index}.txt`.

Requires:
    beautifulsoup4 (install via `pip install beautifulsoup4`)
"""
import os
import sys
from bs4 import BeautifulSoup

RAW_DIR = os.path.join('.', 'raw_quiz_html')
SPLIT_DIR = os.path.join('.', 'split_quiz_html')


def ensure_directories():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(SPLIT_DIR, exist_ok=True)


def process_div(div):
    """
    Apply in-place transformations to a question div:
    - Remove incorrect answer arrows.
    - Change 'correct' -> 'info' and update text.
    - Remove 'wrong_answer' & 'selected_answer' classes and uncheck inputs.
    - Check inputs associated with 'info' spans.
    """
    # Remove any incorrect answer arrows
    for span in div.select('span.answer_arrow.incorrect'):
        span.decompose()

    # Replace 'correct' class with 'info', and 'Correct!' text
    for tag in div.find_all(lambda t: t.has_attr('class') and 'correct' in t['class']):
        tag['class'] = ['info' if cls == 'correct' else cls for cls in tag['class']]
        if tag.string and 'Correct!' in tag.string:
            tag.string = tag.string.replace('Correct!', 'Correct answer')

    # Remove wrong_answer/selected_answer classes and uncheck inputs
    for tag in div.find_all(lambda t: t.has_attr('class') and any(c in ('wrong_answer', 'selected_answer') for c in t['class'])):
        tag['class'] = [cls for cls in tag['class'] if cls not in ('wrong_answer', 'selected_answer')]
        for inp in tag.find_all('input', {'type': ['radio', 'checkbox']}):
            if inp.has_attr('checked'):
                del inp['checked']

    # For info spans, add checked attribute to associated inputs
    for info_span in div.find_all(lambda t: t.name == 'span' and t.has_attr('class') and 'info' in t['class']):
        arrow_id = info_span.get('id')
        if not arrow_id:
            continue
        for inp in div.find_all('input', {'aria-describedby': arrow_id}):
            if inp.get('type') in ('radio', 'checkbox'):
                inp['checked'] = 'checked'


def split_html_file(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    question_divs = soup.select(
        'div.quiz_sortable.question_holder[role="region"][aria-label="Question"]'
    )
    if not question_divs:
        print(f"No question divs found in {input_path}")
        return

    basename = os.path.splitext(os.path.basename(input_path))[0]
    for idx, div in enumerate(question_divs, start=1):
        process_div(div)
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
