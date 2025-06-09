"""
Module: treater.py

Simplifies and restructures HTML body content to produce a cleaner and flatter version,
removing nested and redundant tags, especially <div> and <span> clusters, while preserving text content.

Usage:
    from treater import Treater
    simplified = Treater().simplify_html(html_body_string)
"""

from bs4 import BeautifulSoup, NavigableString, Tag

class Treater:
    def __init__(self):
        pass

    def simplify_html(self, html: str) -> str:
        """Simplifies the HTML content of a <body> tag, flattening structure and removing noise."""
        soup = BeautifulSoup(html, "html.parser")

        for tag_name in ["script", "style", "svg", "noscript", "iframe"]:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        body = soup.body or soup

        self._normalize_tables(body)
        self._flatten_nested_divs(body)
        self._remove_empty_tags(body)

        return str(body)

    def _normalize_tables(self, tag: Tag):
        """Simplifies table structure by unwrapping unnecessary tags."""
        for table in tag.find_all("table"):
            # Unwrap thead, tbody, tfoot, colgroup
            for to_unwrap in table.find_all(["thead", "tbody", "tfoot", "colgroup"]):
                to_unwrap.unwrap()

            # Remove empty rows or rows without visible content
            for tr in table.find_all("tr"):
                if not tr.get_text(strip=True):
                    tr.decompose()
                else:
                    # Ensure <td> and <th> only
                    for td in tr.find_all():
                        if td.name not in ["td", "th"]:
                            td.unwrap()

    def _flatten_nested_divs(self, tag: Tag):
        for child in list(tag.children):
            if isinstance(child, Tag):
                self._flatten_nested_divs(child)
                if child.name in ["div", "span"] and not child.attrs:
                    if all(isinstance(grand, (NavigableString, Tag)) for grand in child.children):
                        child.unwrap()

    def _remove_empty_tags(self, tag: Tag):
        for child in list(tag.find_all(["div", "span", "p", "table"])):
            if not child.get_text(strip=True):
                child.decompose()
