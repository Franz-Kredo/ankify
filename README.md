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
1. Open Canvas and find quiz answers
2. For each question, copy div that looks like this <div role="region" aria-label="Question" class="quiz_sortable question_holder " id="" style="" data-group-id="">
3. Insert each question into its own .txt within `answers_html`
4. Run `ankify.py`
5. Import to Anki from `anki_import` dir (remember to map each question when importing)
6. Now you should have your flashcards
