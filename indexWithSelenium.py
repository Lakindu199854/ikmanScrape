from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Configuration
BASE_URL = "https://ikman.lk/en/ads?query=vitz"
OUTPUT_FILE = "scraped_data.xlsx"
TEXT_FILE = "output.txt"

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Remove this if you want to see browser window
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def extract_details_from_page():
    items = []
    # Wait until listings are loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.normal--2QYVk"))
    )

    blocks = driver.find_elements(By.CSS_SELECTOR, "li.normal--2QYVk")
    for block in blocks:
        try:
            title = block.find_element(By.CSS_SELECTOR, ".heading--2eONR").text
            details = block.find_element(By.CSS_SELECTOR, ".details--1GUIn").text
            items.append({"Title": title, "Details": details})
        except:
            continue
    return items

def scrape_all_pages():
    all_data = []
    driver.get(BASE_URL)

    while True:
        print(f"Scraping: {driver.current_url}")
        all_data.extend(extract_details_from_page())

        try:
            next_button = WebDriverWait(driver, 5).until(
             EC.element_to_be_clickable((By.CSS_SELECTOR, "div.action-button--1O8tU"))
                )
            next_button.click()
            time.sleep(2)
        except:
            print("No more pages.")
            break

    return all_data

if __name__ == "__main__":
    data = scrape_all_pages()

    # Save to Excel
    df = pd.DataFrame(data)
    df.to_excel(OUTPUT_FILE, index=False)

    # Save to TXT
    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        for item in data:
            f.write(f"Title: {item['Title']}, Details: {item['Details']}\n")

    driver.quit()
    print(f"Scraping complete! Data saved to {OUTPUT_FILE} and {TEXT_FILE}")
