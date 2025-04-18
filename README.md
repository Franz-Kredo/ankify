# ankify
Converts Canvas quiz to Anki Flashcards

## Restrictions
- Max 1 questions
- Only checkboxes

## Prerequisites
- Have all choice labels on your custom Anki Card
- Add the Code Highlight Anki Add-on [Plugin url](https://ankiweb.net/shared/info/1415523481)
    - Addon code: 1415523481

## How to use Ankify
1. Open Canvas and find quiz with the answers
2. Find the element with the id of "questions" and copy it
3. Paste the html into `/raw_html_splitter/raw_quiz_html/<name-of-your-file>.txt`
4. Do this for all the quizzes you want to Ankify
5. Run `raw_html_splitter/splitter.py`
6. Copy all files within `/raw_html_splitter/split_quiz_html` to `/answers_html`
7. Run `ankify.py`
8. Import to Anki from `anki_import` dir (remember to map each question when importing)
9. Now you should have your flashcards
