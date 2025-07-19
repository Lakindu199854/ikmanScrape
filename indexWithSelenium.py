from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

import pandas as pd
import time

# Configuration
SITE_URL="https://ikman.lk"
BASE_URL = "https://ikman.lk/en/ads/sri-lanka/vehicles?sort=relevance&buy_now=0&urgent=0&query=raptor&page=1"
OUTPUT_FILE = "scraped_data.xlsx"
TEXT_FILE = "output.txt"

# Set up Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Remove this if you want to see browser window
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
    for i in range(len(blocks)):
        try:
            # Re-fetch the blocks each time due to DOM refresh
            blocks = driver.find_elements(By.CSS_SELECTOR, "li.normal--2QYVk")
            block = blocks[i]

            title = block.find_element(By.CSS_SELECTOR, ".heading--2eONR").text
            details = block.find_element(By.CSS_SELECTOR, ".details--1GUIn").text

            try:
                btn = block.find_element(By.CSS_SELECTOR,"a.card-link--3ssYv")
                driver.execute_script("arguments[0].click();", btn)
                print("Clicked on the listing button....")
                time.sleep(2)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button.contact-section--1qlvP"))
                )

                show_btn = driver.find_element(By.CSS_SELECTOR,"button.contact-section--1qlvP")
                driver.execute_script("arguments[0].click();", show_btn)
                print("Clicked on the call button....")

               # Wait for the phone number to be revealed
                phone = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.phone-numbers--2COKR"))
                ).text


                try:
                    phone = driver.find_element(By.CSS_SELECTOR,"div.phone-numbers--2COKR").text
                except:
                    phone="N/A"
                print(phone)

                driver.back()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.normal--2QYVk"))
                )

            except TimeoutException:
                print("Timeout while loading details page.")
                phone = "N/A"

            items.append({"Title": title, "Details": details, "Phone": phone})
        
        except Exception as e:
            print(f"Error processing block: {e}")
            continue
    return items


def scrape_all_pages():
    all_data = []
    driver.get(BASE_URL)
    page_number = 1

    while True:
        print(f"Scraping page {page_number}: {driver.current_url}")
        current_page_data = extract_details_from_page()

        # Stop if same ads are repeated (pagination is broken)
        if page_number > 1 and current_page_data and all_data[-len(current_page_data):] == current_page_data:
            print("Same listings detected again — stopping.")
            break

        all_data.extend(current_page_data)


        try:
            # Try finding a clickable Next button (5s timeout)
            buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.action-button--1O8tU"))
            )

            next_button = None
            for btn in buttons:
                if "next" in btn.text.strip().lower():
                    next_button = btn
                    break

            if not next_button:
                print("No 'Next' button found — end of pagination.")
                break


            # Scroll and click via JavaScript
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", next_button)
            print("Clicked next... waiting for listings to reload...")

            # Wait for the next batch of listings to appear
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.normal--2QYVk"))
            )

            page_number += 1
            time.sleep(2)

        except TimeoutException:
            print("Next button is no longer clickable — end of pagination.")
            break
        except Exception as e:
            print(f"Unexpected error or page limit reached: {e}")
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
          f.write(f"Title: {item['Title']}, Details: {item['Details']}, Phone: {item['Phone']}\n")


    driver.quit()
    print(f"Scraping complete! Data saved to {OUTPUT_FILE} and {TEXT_FILE}")
