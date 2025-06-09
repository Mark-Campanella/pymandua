"""
Module: aggregator.py

Aggregates multiple HTML pages by appending only new content to a main HTML string.
Avoids duplicating sections already present in the main HTML.

Usage:
    from aggregator import Aggregator
    aggregator = Aggregator()
    main_html = "<html><body><p>Existing</p></body></html>"
    pages = ["<html><body><p>New</p></body></html>", "<html><body><p>Existing</p></body></html>"]
    updated_html = aggregator.update_main_html(main_html, pages)
"""
from bs4 import BeautifulSoup, Tag

class Aggregator:
    def __init__(self):
        pass

    def update_main_html(self, main_html: str, new_html_pages: list) -> str:
        """
        Appends only new content from each HTML string in new_html_pages to the main_html string.
        Content is considered new if its serialized HTML is not already present as a direct child in main_html's <body>.

        Args:
            main_html (str): The base HTML string to which new content will be appended.
            new_html_pages (list): List of HTML strings to merge into main_html.

        Returns:
            str: Updated HTML string containing main content plus unique additions.
        """
        main_soup = BeautifulSoup(main_html, "html.parser")
        main_body = main_soup.body or main_soup

        # Collect serialized strings of existing direct children in main_body
        existing_serials = set()
        for child in list(main_body.children):
            if isinstance(child, Tag):
                existing_serials.add(child.encode_contents().decode("utf-8").strip())
            else:
                text = str(child).strip()
                if text:
                    existing_serials.add(text)

        # Iterate through each new HTML page
        for html in new_html_pages:
            new_soup = BeautifulSoup(html, "html.parser")
            new_body = new_soup.body or new_soup
            for child in list(new_body.children):
                # Serialize each direct child of new_body
                if isinstance(child, Tag):
                    serialized = child.encode_contents().decode("utf-8").strip()
                    if serialized and serialized not in existing_serials:
                        # Append deepcopy of the tag to main_body
                        main_body.append(child)
                        existing_serials.add(serialized)
                else:
                    text = str(child).strip()
                    if text and text not in existing_serials:
                        main_body.append(text)
                        existing_serials.add(text)

        return str(main_soup)
