import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://ikman.lk/en/ads?query=vitz"  # 🔁 Replace with target site
HEADERS = {"User-Agent": "Mozilla/5.0"}  # To avoid being blocked
OUTPUT_FILE = "scraped_data.xlsx"

def extract_details(soup):
    items=[]
    for block in soup.select(".normal--2QYVk"):

        title=block.select_one(".heading--2eONR").get_text(strip=True)
        details=block.select_one(".details--1GUIn").get_text(strip=True)

        print(title);
        items.append({"title":title,"details":details})
    return items

def scrape_all_pages(start_url):
    all_data=[]
    current_url=start_url

    while current_url:
        print(f"Scraping {current_url}")
        response = requests.get(current_url,headers=HEADERS)
        soup=BeautifulSoup(response.content,"html.parser")
        all_data.extend(extract_details(soup))

        next_link=soup.select_one(".action-button--1O8tU");
        if next_link:
            current_url=urljoin(current_url,next_link['href'])
        else:
            break;
            
    return all_data

if __name__ == "__main__":
    data = scrape_all_pages(BASE_URL)
    df = pd.DataFrame(data)
    with open("output.txt", "w", encoding="utf-8") as f:
        for item in data:
            f.write(f"Title: {item['Title']}, Price: {item['Price']}\n")

    print(f"Scraping complete! Data saved to {OUTPUT_FILE}")
