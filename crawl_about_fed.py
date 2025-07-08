# crawl_about_fed.py

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://www.federalreserve.gov"
START_URL = f"{BASE_URL}/aboutthefed.htm"
OUTPUT_DIR = "about_the_fed_pages"
os.makedirs(OUTPUT_DIR, exist_ok=True)

visited = set()
to_visit = [START_URL]
max_pages = 1000  # increased to allow deeper crawling

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n").strip()

count = 0
while to_visit and count < max_pages:
    url = to_visit.pop(0)

    # Normalize: remove fragments (#) and query params (?)
    url = url.split("#")[0].split("?")[0]

    if url in visited:
        continue

    try:
        print(f"🔗 Fetching: {url}")
        r = requests.get(url, timeout=10)
        print(f"   ↪ Status: {r.status_code}, Content-Type: {r.headers.get('Content-Type')}")

        if r.status_code != 200:
            continue

        visited.add(url)
        text = extract_text(r.text)
        word_count = len(text.split())

        if word_count < 30:
            print("   ⚠️ Skipping — too short")
            continue

        # Save to file
        path = urlparse(url).path.strip("/")
        slug = path.replace("/", "_").replace(".htm", "").replace(".html", "")
        filename = os.path.join(OUTPUT_DIR, f"{slug if slug else 'aboutthefed_index'}.txt")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"<!-- {url} -->\n")
            f.write(text)

        print(f"✅ Saved: {filename}")
        count += 1

        # Add more crawlable links
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(BASE_URL, href)
            if (
                full_url.startswith(f"{BASE_URL}/aboutthefed/") and
                full_url.endswith((".htm", ".html")) and
                "currencies" not in full_url and
                "frb" not in full_url
            ):
                clean_url = full_url.split("#")[0].split("?")[0]
                if clean_url not in visited and clean_url not in to_visit:
                    to_visit.append(clean_url)

        time.sleep(0.3)

    except Exception as e:
        print(f"❌ Error at {url}: {e}")
