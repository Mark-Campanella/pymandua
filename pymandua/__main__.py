import argparse
from . import to_mkd

parser = argparse.ArgumentParser(description="Convert HTML pages to Markdown.")
parser.add_argument("--urls",   nargs="+", required=True, help="One or more URLs to scrape.")
parser.add_argument("--keywords", nargs="+", default=None,
                    help="Fuzzy‐match keywords for clickable navigation (e.g. Next, Continue).")
parser.add_argument("--output", default=None, help="Output folder (defaults to ./output).")
parser.add_argument("--wait", type=float, default=2.0, help="Seconds to wait after navigation.")
parser.add_argument("--threshold", type=float, default=80.0,
                    help="Fuzzy match threshold (0–100).")
args = parser.parse_args()

to_mkd(
    urls=args.urls,
    keywords=args.keywords,
    output_path=args.output,
    wait=args.wait,
    threshold=args.threshold,
)
