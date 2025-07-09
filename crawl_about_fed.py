import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
from datetime import datetime

BASE_URL = "https://www.federalreserve.gov"
START_URL = f"{BASE_URL}/aboutthefed.htm"
SAVE_DIR = "about_the_fed_pages"
MAX_PAGES = 1500
CONCURRENCY = 10
SEEN = set()

os.makedirs(SAVE_DIR, exist_ok=True)

def is_valid_url(href):
    return href and href.startswith("/aboutthefed") and not href.endswith(".pdf")

def clean_soup(soup):
    for tag in soup(["header", "nav", "footer", "script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

def extract_main_content(html):
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one("div#content") or soup.select_one("main") or soup.select_one("body")
    if not container:
        return None, None
    text = clean_soup(container)
    title = soup.title.string.strip() if soup.title else "Untitled"
    return title, text

async def fetch(session, url):
    try:
        async with session.get(url, timeout=20) as response:
            if response.content_type != "text/html":
                return None
            return await response.text()
    except Exception as e:
        print(f"[ERROR] Fetching {url}: {e}")
        return None

async def crawl_page(session, url, queue):
    if url in SEEN or len(SEEN) >= MAX_PAGES:
        return
    SEEN.add(url)

    html = await fetch(session, url)
    if not html:
        return

    title, content = extract_main_content(html)
    if not content or len(content.strip()) < 100:
        print(f"[SKIP] {url} (too short or empty)")
        return

    filename = url.replace(BASE_URL, "").strip("/").replace("/", "_") + ".txt"
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"<!-- source_url: {url} -->\n")
        f.write(f"<!-- title: {title} -->\n")
        f.write(f"<!-- date_fetched: {datetime.utcnow().isoformat()}Z -->\n\n")
        f.write(content)

    print(f"[✓] Saved: {filename}")

    # Enqueue new links
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(BASE_URL, href)
        if is_valid_url(href) and full_url not in SEEN:
            await queue.put(full_url)

async def worker(queue, session):
    while True:
        url = await queue.get()
        await crawl_page(session, url, queue)
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    await queue.put(START_URL)

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(worker(queue, session)) for _ in range(CONCURRENCY)]
        await queue.join()
        for task in tasks:
            task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
