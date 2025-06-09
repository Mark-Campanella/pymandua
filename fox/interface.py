# html2mkd/_core.py

import os
import time
from datetime import datetime
from typing import List, Union

from .driver        import Driver, DriverUtils
from .gatherer      import Gatherer
from .treater       import Treater
from .cleaner       import Cleaner
from .crawler       import Crawler
from .aggregator    import Aggregator
from .converter     import HTMLToMarkdownConverter


this_file = os.path.abspath(__file__)
src_folder = os.path.dirname(this_file)           # “…/Web-Scraper-with-AI/src/fox”
src_root = os.path.dirname(src_folder)             # “…/Web-Scraper-with-AI/src”
project_root = os.path.dirname(src_root)           # “…/Web-Scraper-with-AI”

def to_mkd(
    urls: Union[str, List[str]],
    keywords: Union[str, List[str]],
    output_path: Union[str, None] = None,
    wait: float = 2.0,
    threshold: float = 95.0
) -> str:
    """
    Converts HTML from given URLs to a single Markdown file.

    Args:
        urls (str or List[str]):
            A single URL or list of URLs to scrape.
        keywords (str or List[str]):
            A single keyword or list of keywords to use for fuzzy-matching clickable
            links/buttons (e.g. ["Next", "Continue"]). If None, no crawling is done.
        output_path (str or None):
            Directory where the .mkd file will be saved. If None, defaults to ./output.
        wait (float):
            Seconds to wait after clicking/navigating before gathering HTML.
        threshold (float):
            Minimum fuzzy match score (0–100) to consider something a match.

    Returns:
        The full Markdown string that was written to disk.
    """
    # Ensure we have a list of URLs and a list of keywords
    if isinstance(urls, str):
        urls = [urls]
    if isinstance(keywords, str):
        keywords = [keywords]

    driver = None
    all_html_fragments = []  # we'll accumulate HTML from each URL + its related pages

    try:
        # 1) Initialize WebDriver once:
        driver = Driver().init()
        driver_tools = DriverUtils(driver)

        # We'll loop over each URL and gather HTML (and any crawled pages)
        for url in urls:
            driver.get(url)
            time.sleep(wait)  # give browser a moment

            # 2) Gather initial raw HTML for this URL
            gatherer = Gatherer(driver)
            raw_html_main = gatherer.get_body_html()

            # 3) If keywords are provided, attempt to crawl
            if keywords:
                crawler = Crawler(driver, gatherer, keywords, wait=wait, threshold=threshold)
                related_htmls = crawler.crawl()

                # 4) Aggregate the newly found pages into the “main” HTML
                aggregator = Aggregator()
                raw_html_main = aggregator.update_main_html(raw_html_main, related_htmls)

            all_html_fragments.append(raw_html_main)

    except Exception as e:
        # If anything goes wrong at this stage, ensure driver closes and re‐raise
        print(f"[fox] Error during browsing & crawling: {e}")
        raise

    finally:
        # 5) Close the driver (if we ever opened it)
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    # At this point, all_html_fragments is a list of full HTML bodies (string) for each URL (plus related pages)
    # We can merge them into one big “raw_html” before treating/cleaning/converting
    combined_html = "<html><body>"
    for fragment in all_html_fragments:
        # We assume each fragment is a full <html>… with <body>. We only want the inside of <body>.
        # Use BeautifulSoup (via your Treater) or a quick string‐split. For safety, let's rely on Treater to strip outer tags:
        treater = Treater()
        body_only = treater.simplify_html(fragment)  # this yields something like "<body>…</body>"
        # Append the contents of that <body> into our combined_html
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(body_only, "html.parser")
        for child in soup.body.children:
            combined_html += str(child)
    combined_html += "</body></html>"

    # 6) Flatten + clean the combined HTML
    treater = Treater()
    treated_html = treater.simplify_html(combined_html)

    cleaner = Cleaner()
    cleaned_html = cleaner.clean(treated_html)

    # 7) Convert to Markdown
    converter = HTMLToMarkdownConverter()
    markdown = converter.convert(cleaned_html)

    # 8) Write out to disk
    if output_path:
        # If user explicitly passed a path, use it (absolute or relative).
        output_folder = output_path
    else:
        # Otherwise, always create/use “project-root/output/”
        output_folder = os.path.join(project_root, "output")
        os.makedirs(output_folder, exist_ok=True)

    # Finally, build the full path for the .mkd
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    filename  = f"output_{timestamp}.mkd"
    full_path = os.path.join(output_folder, filename)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"[html2mkd] Markdown file saved at: {full_path}")
    return markdown
