from flask import redirect, render_template, session
from functools import wraps
from nltk.tokenize import sent_tokenize
import re

def login_required(f):
    # Taken from "CS50 Finance" Problem Set
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def sentence_count(text: str) -> int:
    # Adaptation from function found in Stack Overflow
    # Posted by Preetkaran Singh
    # Source: https://stackoverflow.com/questions/15228054/how-to-count-the-amount-of-sentences-in-a-paragraph-in-python
    return len(sent_tokenize(text))

def word_count(text: str) -> int:
    # Adaptation from funtion found in Geeks for Geeks
    # Source: https://www.geeksforgeeks.org/python/python-program-to-count-words-in-a-sentence/
    words = re.findall(r'\b\w+\b', text)
    return len(words)

def line_count(text: str) -> int:
    lines = text.splitlines()
    return len(lines)

def paragraph_count(text: str) -> int:
    paragraphs = [p for p in text.split("\n") if p.strip()]
    return len(paragraphs)
