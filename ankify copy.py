#!/Applications/MAMP/htdocs/venv/bin/python
import os
import hashlib
from bs4 import BeautifulSoup

def compute_checksum(content: str) -> str:
    """Compute MD5 checksum for a given string content."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def main():
    # Define directories
    answers_dir = "answers_html"
    questions_dir = "questions_html"
    anki_imports_dir = "anki_imports"
    
    # Ensure necessary directories exist
    for d in (questions_dir, anki_imports_dir):
        if not os.path.exists(d):
            os.makedirs(d)
    
    # Determine the next anki_import file name by checking existing increments
    max_inc = 0
    for f in os.listdir(anki_imports_dir):
        if f.startswith("anki_import") and f.endswith(".txt"):
            try:
                num = int(f[len("anki_import"):-len(".txt")])
                if num > max_inc:
                    max_inc = num
            except ValueError:
                continue
    new_inc = max_inc + 1
    anki_import_filename = f"anki_import{new_inc}.txt"
    anki_import_filepath = os.path.join(anki_imports_dir, anki_import_filename)
    
    # Open the new import file for writing (UTF-8 plain text)
    with open(anki_import_filepath, 'w', encoding='utf-8') as anki_file:
        # Write the file header as per documentation
        anki_file.write("#separator:pipe\n")
        anki_file.write("#html:true\n")
        anki_file.write("#notetype:CanvasQuizCards\n")
        # (Optionally, define additional headers such as deck, columns, etc.)
        
        # Process each answer file in the answers_html directory
        for answer_filename in os.listdir(answers_dir):
            if not answer_filename.endswith('.txt'):
                continue
            
            answer_filepath = os.path.join(answers_dir, answer_filename)
            try:
                with open(answer_filepath, 'r', encoding='utf-8') as f:
                    answer_content = f.read()
            except FileNotFoundError:
                print(f"Error: {answer_filepath} does not exist.")
                continue
            
            # Perform the necessary string replacements
            answer_content = answer_content.replace(
                '/dist/images/answers_sprite-0d764f2477.png',
                'https://du11hjcvx0uqb.cloudfront.net/dist/images/answers_sprite-0d764f2477.png'
            )
            answer_content = answer_content.replace('disabled=""', '')
            
            # Use BeautifulSoup to modify HTML content for the question field
            soup = BeautifulSoup(answer_content, "html.parser")
            
            # Remove unwanted elements (example: .answer_arrow and .quiz_comment)
            for tag in soup.select(".answer_arrow, .quiz_comment"):
                tag.decompose()
            
            # Remove the "title" attribute from all <div> tags
            for div in soup.find_all('div'):
                if div.has_attr('title'):
                    del div['title']
            
            # Deselect all radio and checkbox inputs by removing the "checked" attribute
            for input_tag in soup.find_all('input'):
                if input_tag.get('type') in ['radio', 'checkbox'] and input_tag.has_attr('checked'):
                    del input_tag['checked']
            
            # Convert the modified soup back to a string (this is our question field)
            processed_html = str(soup)
            
            # Compute checksum for the processed (question) content so duplicates can be avoided.
            new_checksum = compute_checksum(processed_html)
            
            # Build the corresponding question file name in questions_html (prefixed with "question_")
            question_filename = f"question_{answer_filename}"
            question_filepath = os.path.join(questions_dir, question_filename)
            
            duplicate_found = False
            if os.path.exists(question_filepath):
                try:
                    with open(question_filepath, 'r', encoding='utf-8') as qf:
                        existing_content = qf.read()
                    if compute_checksum(existing_content) == new_checksum:
                        duplicate_found = True
                        print(f"Identical file detected for {answer_filename}: using existing question file {question_filepath}.")
                except Exception as e:
                    print(f"Error reading {question_filepath}: {e}")
            
            # Write out the new question file if not a duplicate.
            if not duplicate_found:
                try:
                    with open(question_filepath, 'w', encoding='utf-8') as qf:
                        qf.write(processed_html)
                    print(f"Question file written: {question_filepath}")
                except Exception as e:
                    print(f"Error writing to {question_filepath}: {e}")
            
            # Generate the Anki card line
            try:
                with open(question_filepath, 'r', encoding='utf-8') as qf:
                    question_field = qf.read()
                # Read the answer from the original answer file (keeping its original HTML)
                with open(answer_filepath, 'r', encoding='utf-8') as af:
                    answer_field = af.read()
            except Exception as e:
                print(f"Error reading card content for {answer_filename}: {e}")
                continue
            
            # Ensure that both question and answer fields are rendered as a one-line HTML:
            question_line = " ".join(question_field.split())
            answer_line = " ".join(answer_field.split())
            
            # --- New Section: Extract the answer choices ---
            # Parse the answer file to extract each answer's text from elements with class "answer_text"
            soup_choices = BeautifulSoup(answer_field, "html.parser")
            answer_text_divs = soup_choices.select(".answers_wrapper .answer_text")
            choices_list = [div.get_text(strip=True) for div in answer_text_divs]
            # Use only the first 10 choices; if fewer than 10, pad with empty strings.
            choices_list = choices_list[:10]
            while len(choices_list) < 10:
                choices_list.append("")
            
            # Construct the card line including the actual choices using dynamic join:
            choices_formatted = "".join(f"|{choice}" for choice in choices_list)
            card_line = f"CanvasQuizCards|{question_line}|{answer_line}{choices_formatted}|\n"
            anki_file.write(card_line)
    
    print(f"Anki import file generated at: {anki_import_filepath}")

if __name__ == "__main__":
    main()