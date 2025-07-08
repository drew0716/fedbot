import os
import requests
import datetime
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm


BASE_URL = "https://www.federalreserve.gov"
FOMC_CALENDAR = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
DOWNLOAD_DIR = "fed_pdfs"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_fomc_pdfs():
    response = requests.get(FOMC_CALENDAR)
    soup = BeautifulSoup(response.text, "html.parser")

    pdf_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "monetarypolicy/files/" in href and href.endswith(".pdf"):
            full_url = urljoin(BASE_URL, href)
            pdf_links.append(full_url)

    for url in pdf_links:
        filename = os.path.join(DOWNLOAD_DIR, url.split("/")[-1])
        if not os.path.exists(filename):
            print(f"Downloading {url}")
            r = requests.get(url)
            with open(filename, "wb") as f:
                f.write(r.content)
        else:
            print(f"Already downloaded {filename}")

def download_press_releases_via_rss():
    print("📡 Fetching press releases via RSS...")
    RSS_URL = "https://www.federalreserve.gov/feeds/press_all.xml"
    press_dir = os.path.join(DOWNLOAD_DIR, "press_releases")
    os.makedirs(press_dir, exist_ok=True)

    feed = feedparser.parse(RSS_URL)
    count = 0

    for entry in feed.entries:
        url = entry.link
        slug = url.split("/")[-1].replace(".htm", "")
        filename = f"{slug}.txt"
        filepath = os.path.join(press_dir, filename)

        if not os.path.exists(filepath):
            try:
                resp = requests.get(url)
                soup = BeautifulSoup(resp.text, "html.parser")

                # Try extracting main content
                article = soup.find("div", class_="col-xs-12 col-sm-8") or soup.find("div", {"id": "article"})

                if article:
                    text = article.get_text(separator="\n").strip()
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(text)
                    count += 1
                else:
                    print(f"⚠️ No article content found at {url}")
            except Exception as e:
                print(f"⚠️ Failed to process {url}: {e}")

    print(f"✅ Downloaded {count} press releases to {press_dir}")

if __name__ == "__main__":
    download_fomc_pdfs()
    download_press_releases_via_rss()