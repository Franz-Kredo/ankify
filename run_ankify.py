#!/Applications/MAMP/htdocs/venv/bin/python
import os
import re
import hashlib
from bs4 import BeautifulSoup


def compute_checksum(content: str) -> str:
    """Compute MD5 checksum for a given string content."""
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def convert_pre_code(html: str) -> str:
    """Wrap <pre> blocks with <code> tags and normalise line‑break markup inside code blocks.

    * <pre>       → <pre><code>
    * </pre>      → </code></pre>
    * Inside <code> … </code> replace <br> / &lt;br&gt; with &#10;
    """
    if not html:
        return html

    # Ensure every <pre> has a nested <code>
    html = html.replace("<pre>", "<pre><code>").replace("</pre>", "</code></pre>")

    # Replace <br> variations inside each individual <code> … </code>
    def _fix_br(match: re.Match) -> str:
        inner = match.group(1)
        inner = re.sub(r"(<br\s*/?>|&lt;br\s*/?&gt;)", "&#10;", inner, flags=re.IGNORECASE)
        return f"<code>{inner}</code>"

    html = re.sub(r"<code>(.*?)</code>", _fix_br, html, flags=re.DOTALL | re.IGNORECASE)
    return html


def main():
    # Define directories
    answers_dir = "answers_html"
    questions_dir = "questions_html"
    anki_imports_dir = "anki_imports"

    # Ensure necessary directories exist
    for d in (questions_dir, anki_imports_dir):
        os.makedirs(d, exist_ok=True)

    # Determine the next anki_import file name by checking existing increments
    max_inc = 0
    for f in os.listdir(anki_imports_dir):
        if f.startswith("anki_import") and f.endswith(".txt"):
            try:
                num = int(f[len("anki_import"):-len(".txt")])
                max_inc = max(max_inc, num)
            except ValueError:
                continue
    new_inc = max_inc + 1
    anki_import_filepath = os.path.join(anki_imports_dir, f"anki_import{new_inc}.txt")

    with open(anki_import_filepath, "w", encoding="utf-8") as anki_file:
        # Anki‑import header
        anki_file.write("#separator:pipe\n#html:true\n#notetype:CanvasQuizCards\n")

        # Process every answer file
        for answer_filename in os.listdir(answers_dir):
            if not answer_filename.endswith(".txt"):
                continue

            answer_filepath = os.path.join(answers_dir, answer_filename)
            try:
                with open(answer_filepath, "r", encoding="utf-8") as f:
                    answer_content = f.read()
            except FileNotFoundError:
                print(f"Error: {answer_filepath} does not exist.")
                continue

            # --- Static replacements ---
            answer_content = answer_content.replace(
                "/dist/images/answers_sprite-0d764f2477.png",
                "https://du11hjcvx0uqb.cloudfront.net/dist/images/answers_sprite-0d764f2477.png",
            ).replace("disabled=\"\"", "")

            # --- NEW: code‑block normalisation ---
            answer_content = convert_pre_code(answer_content)

            # Build soup for question‑side cleaning
            soup = BeautifulSoup(answer_content, "html.parser")

            # Remove unwanted elements
            for tag in soup.select(".answer_arrow, .quiz_comment"):
                tag.decompose()

            # Remove title attributes on <div>
            for div in soup.find_all("div"):
                div.attrs.pop("title", None)

            # Un‑check radio/checkbox inputs
            for inp in soup.find_all("input", {"type": ["radio", "checkbox"]}):
                inp.attrs.pop("checked", None)

            # Convert to string & escape literal newlines
            processed_html = str(soup).replace("\n", "&#10;")

            # Checksum to detect duplicates
            new_checksum = compute_checksum(processed_html)
            question_filename = f"question_{answer_filename}"
            question_filepath = os.path.join(questions_dir, question_filename)

            duplicate_found = False
            if os.path.exists(question_filepath):
                with open(question_filepath, "r", encoding="utf-8") as qf:
                    if compute_checksum(qf.read()) == new_checksum:
                        duplicate_found = True
                        print(f"Identical file detected for {answer_filename}; using existing question file.")

            if not duplicate_found:
                try:
                    with open(question_filepath, "w", encoding="utf-8") as qf:
                        qf.write(processed_html)
                    print(f"Question file written: {question_filepath}")
                except Exception as e:
                    print(f"Error writing {question_filepath}: {e}")

            # --- Build Anki card line ---
            question_line = " ".join(processed_html.split())
            answer_line = " ".join(answer_content.split())

            # Extract answer choices (max 10)
            soup_choices = BeautifulSoup(answer_content, "html.parser")
            choices = [d.get_text(strip=True) for d in soup_choices.select(".answers_wrapper .answer_text")][:10]
            choices.extend([""] * (10 - len(choices)))
            choices_formatted = "".join(f"|{c}" for c in choices)

            anki_file.write(f"CanvasQuizCards|{question_line}|{answer_line}{choices_formatted}|\n")

    print(f"Anki import file generated at: {anki_import_filepath}")


if __name__ == "__main__":
    main()
