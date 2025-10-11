"""
Module: converter.py

Converts cleaned and treated HTML into a simplified Markdown format,
designed to be easily interpreted by LLMs.

Usage:
    from converter import HTMLToMarkdownConverter
    markdown = HTMLToMarkdownConverter().convert(html_string)
"""

from bs4 import BeautifulSoup

class Converter:
    def __init__(self):
        pass

    def convert(self, html: str) -> str:
        """Converts simplified HTML into a markdown-like string."""
        soup = BeautifulSoup(html, "html.parser")
        return self._parse_children(soup).strip()

    def _parse_children(self, tag) -> str:
        """
        Recursively traverses the children of an HTML tag and converts each to a simplified
        Markdown-like format, suitable for Large Language Models (LLMs).

        Supports the following elements:
        - Headers <h1> to <h6>: converted to lines with #.
        - Paragraphs <p>: converted to text blocks with spacing.
        - Line breaks <br>: converted to new lines.
        - Emphasis <b>/<strong>, <i>/<em>: converted to **bold** or *italic*.
        - Links <a>: converted to [text](url).
        - Lists <ul>/<ol>: converted to lists with "-" or "1." etc.
        - Code blocks <pre>/<code>: converted to markdown blocks (``` or `).
        - Tables <table>: converted via the _convert_table_to_markdown method.
        - Unknown tags: processed recursively.

        Parameters:
            tag (bs4.element.Tag): The root HTML tag whose children will be processed.

        Returns:
            str: A Markdown-like representation of the tag's content.
        """
        markdown = ""

        for element in tag.children:
            if isinstance(element, str):
                # Plain text content between the tags
                markdown += element.strip()
                continue

            match element.name:
                case "h1" | "h2" | "h3" | "h4" | "h5" | "h6":
                    level = int(element.name[1])
                    markdown += f"\n{'#' * level} {element.get_text(strip=True)}\n\n"

                case "p":
                    markdown += f"\n{element.get_text(strip=True)}\n\n"

                case "br":
                    markdown += "\n"

                case "strong" | "b":
                    markdown += f"**{element.get_text(strip=True)}**"

                case "em" | "i":
                    markdown += f"*{element.get_text(strip=True)}*"

                case "a":
                    href = element.get("href", "")
                    text = element.get_text(strip=True)
                    markdown += f"[{text}]({href})"

                case "ul":
                    for li in element.find_all("li", recursive=False):
                        markdown += f"- {li.get_text(strip=True)}\n"
                    markdown += "\n"

                case "ol":
                    for i, li in enumerate(element.find_all("li", recursive=False), start=1):
                        markdown += f"{i}. {li.get_text(strip=True)}\n"
                    markdown += "\n"

                case "code":
                    markdown += f"`{element.get_text(strip=True)}`"

                case "pre":
                    code = element.get_text()
                    markdown += f"\n```\n{code}\n```\n"

                case "table":
                    markdown += self._convert_table_to_markdown(element)

                case _:
                    markdown += self._parse_children(element)

        return markdown

    def _convert_table_to_markdown(self, table) -> str:
        """
        Converts a <table> HTML element into a markdown-formatted table.

        Parameters:
            table (bs4.element.Tag): The <table> tag to convert.

        Returns:
            str: Markdown representation of the table.
        """
        rows = table.find_all("tr")
        if not rows:
            return ""

        header_cells = rows[0].find_all(["th", "td"])
        headers = [cell.get_text(strip=True) for cell in header_cells]
        markdown = "| " + " | ".join(headers) + " |\n"
        markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            values = [cell.get_text(strip=True) for cell in cells]
            markdown += "| " + " | ".join(values) + " |\n"

        return "\n" + markdown + "\n"
