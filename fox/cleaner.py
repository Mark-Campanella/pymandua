"""
Module: cleaner.py

Performs general cleanup on raw HTML strings before structural simplification.
Removes unwanted metadata, normalizes line breaks, and keeps useful attributes like class and href.

Usage:
    from cleaner import HTMLCleaner
    cleaned_html = HTMLCleaner().clean(raw_html_string)
"""

from bs4 import BeautifulSoup, Comment

class Cleaner:
    def __init__(self, keep_attrs=None):
        # Atributos que serão mantidos nas tags (pode ser customizado)
        self.keep_attrs = keep_attrs or {"class", "href", "src", "alt", "title"}

    def clean(self, html: str) -> str:
        """Cleans raw HTML to remove noise and normalize structure."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove <head> e metadados
        if soup.head:
            soup.head.decompose()

        # Remove comentários
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove tags que normalmente não são úteis
        for tag_name in [
            "script", "style", "svg", "noscript", "iframe",
            "header", "footer", "nav", "form", "input", "button"
        ]:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Limpa os atributos, mantendo apenas os definidos
        for tag in soup.find_all():
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in self.keep_attrs}

        # Normaliza espaços
        text = str(soup)
        text = text.replace('\xa0', ' ')  # Non-breaking space
        text = '\n'.join(line.strip() for line in text.splitlines())
        text = '\n'.join([line for line in text.split('\n') if line.strip()])  # Remove linhas vazias

        return text
