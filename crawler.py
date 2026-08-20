import requests
import json
import time
import os
import argparse

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from collections import deque


def normalize_url(url):
    parsed = urlparse(url)

    # Add https if user only enters example.com
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    path = parsed.path.rstrip("/")

    clean_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        path,
        "",
        parsed.query,
        ""
    ))

    # Keep homepage clean
    if path == "":
        clean_url = f"{parsed.scheme}://{parsed.netloc}"

    return clean_url


def get_robots(url):
    parsed = urlparse(url)

    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    robots = RobotFileParser()
    robots.set_url(robots_url)

    try:
        robots.read()
        print("[+] Loaded robots.txt")
        print(f"    {robots_url}")
    except Exception as error:
        print("[!] Could not load robots.txt")
        print(f"    {error}")

    return robots


def get_page(url, user_agent):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": user_agent
            }
        )

        if response.status_code != 200:
            print(f"[!] Skipped ({response.status_code})")
            return None

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type:
            print("[!] Skipped non-HTML page")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Get page title
        if soup.title:
            title = soup.title.get_text(strip=True)
        else:
            title = "No title"

        # Get page description
        description = ""

        description_tag = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if description_tag:
            description = description_tag.get(
                "content",
                ""
            ).strip()

        # Remove things we don't need from page text
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(" ", strip=True)

        links = []

        # Find all links
        for link in soup.find_all("a", href=True):
            href = link.get("href")

            # Skip links that don't lead to webpages
            if href.startswith((
                "#",
                "javascript:",
                "mailto:",
                "tel:"
            )):
                continue

            full_url = urljoin(url, href)
            full_url = normalize_url(full_url)

            # Only allow normal web URLs
            if not full_url.startswith(("http://", "https://")):
                continue

            # Prevent duplicate links on same page
            if full_url not in links:
                links.append(full_url)

        return {
            "url": url,
            "title": title,
            "description": description,
            "text": text,
            "links": links,
            "status": response.status_code
        }

    except requests.RequestException as error:
        print(f"[!] Error while crawling:")
        print(f"    {error}")
        return None


def save_results(results, output_file):
    folder = os.path.dirname(output_file)

    # Create output folder if needed
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print(f"[+] Results saved to: {output_file}")


def crawl(start_url, max_pages, delay, output_file, user_agent):
    visited = set()
    queue = deque()
    results = []

    start_url = normalize_url(start_url)
    start_domain = urlparse(start_url).netloc

    robots = get_robots(start_url)

    queue.append(start_url)

    print()
    print("=" * 45)
    print("              CLIGRABER")
    print("        Simple Python Web Crawler")
    print("=" * 45)
    print(f"Target    : {start_url}")
    print(f"Max pages : {max_pages}")
    print(f"Delay     : {delay}s")
    print("=" * 45)

    while queue and len(visited) < max_pages:

        current_url = queue.popleft()

        # Don't crawl same page twice
        if current_url in visited:
            continue

        # Respect robots.txt
        if not robots.can_fetch(user_agent, current_url):
            print(f"[BLOCKED] {current_url}")
            visited.add(current_url)
            continue

        page_number = len(visited) + 1

        print()
        print(f"[{page_number}/{max_pages}] Crawling")
        print(current_url)

        # Add before request so failed URLs don't get retried forever
        visited.add(current_url)

        page = get_page(current_url, user_agent)

        if page:
            results.append(page)

            # Add new same-domain links to queue
            for link in page["links"]:
                parsed_link = urlparse(link)

                if parsed_link.netloc != start_domain:
                    continue

                if link not in visited and link not in queue:
                    queue.append(link)

        # Wait before next request
        if queue:
            time.sleep(delay)

    save_results(results, output_file)

    print()
    print("=" * 45)
    print("          CRAWL FINISHED")
    print("=" * 45)
    print(f"Pages visited : {len(visited)}")
    print(f"Pages saved   : {len(results)}")
    print(f"URLs left     : {len(queue)}")
    print(f"Output        : {output_file}")
    print("=" * 45)


def main():
    parser = argparse.ArgumentParser(
        prog="CLIgraber",
        description="CLIgraber - A simple command-line web crawler made with Python"
    )

    parser.add_argument(
        "url",
        help="Website URL to crawl"
    )

    parser.add_argument(
        "--max-pages",
        "-m",
        type=int,
        default=20,
        help="Maximum number of pages to crawl (default: 20)"
    )

    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1,
        help="Delay between requests in seconds (default: 1)"
    )

    parser.add_argument(
        "--output",
        "-o",
        default="data/crawl_results.json",
        help="JSON file where results will be saved"
    )

    parser.add_argument(
        "--user-agent",
        default="CLIgraber/1.0",
        help="Custom User-Agent for requests"
    )

    args = parser.parse_args()

    # Basic input validation
    if args.max_pages <= 0:
        print("[!] Max pages must be more than 0")
        return

    if args.delay < 0:
        print("[!] Delay cannot be negative")
        return

    crawl(
        args.url,
        args.max_pages,
        args.delay,
        args.output,
        args.user_agent
    )


if __name__ == "__main__":
    main()