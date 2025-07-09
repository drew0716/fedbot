import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://www.federalreserve.gov"
START_URL = f"{BASE_URL}/aboutthefed.htm"
OUTPUT_DIR = "about_the_fed_pages"
VISITED = set()
MAX_PAGES = 1500
SLEEP_TIME = 0.1  # Be polite

def extract_main_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Find the main content container
    main_content = soup.find("div", id="content", class_="container container__main")

    if main_content:
        text = main_content.get_text(separator="\n", strip=True)
    else:
        print("[WARN] Could not find main content. Falling back to full page.")
        text = soup.get_text(separator="\n", strip=True)

    return clean_text(text)

def clean_text(text: str) -> str:
    # Remove known boilerplate lines
    lines = text.splitlines()
    cleaned = [
        line for line in lines
        if line.strip() and not any(phrase in line.lower() for phrase in [
            "official website", "javascript", "back to top", "privacy policy",
            "subscribe to", "site map", "contact", "faq", "stay connected"
        ])
    ]
    return "\n".join(cleaned).strip()

def is_valid_link(href: str) -> bool:
    if not href:
        return False
    if href.startswith("#") or "mailto:" in href or "javascript:" in href:
        return False
    return "/aboutthefed" in href

def save_page(url: str, content: str):
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    if not path:
        path = "index"
    filename = os.path.join(OUTPUT_DIR, f"{path}.txt")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Saved: {filename}")

def crawl(url: str):
    if url in VISITED or len(VISITED) >= MAX_PAGES:
        return
    VISITED.add(url)

    try:
        response = requests.get(url)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            print(f"⛔ Skipped: {url} (status: {response.status_code})")
            return

        print(f"🔗 Fetching: {url}")
        content = extract_main_content(response.text)
        save_page(url, content)

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if is_valid_link(href):
                next_url = urljoin(BASE_URL, href)
                crawl(next_url)
                time.sleep(SLEEP_TIME)

    except Exception as e:
        print(f"❌ Error crawling {url}: {e}")

if __name__ == "__main__":
    crawl(START_URL)
