import time
import random
import csv
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# ✅ SET YOUR CHROMEDRIVER PATH
CHROMEDRIVER_PATH = "C:\\Users\\rakib\\OneDrive\\Desktop\\project\\Scraper\\chromedriver.exe"  # Update this path

# ✅ Initialize Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in background (remove if you want a visible browser)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# ✅ Function to Scrape YellowPages
def scrape_yellowpages(search_term, location):
    data = []
    page_count = 1
    encoded_search= urllib.parse.quote(search_term)
    encoded_location = urllib.parse.quote(location)

    while True:
        url = f"https://www.yellowpages.com/search?search_terms={encoded_search}&geo_location_terms={encoded_location}&page={page_count}"
        print(f"Scraping: {url}")

        driver.get(url)
        time.sleep(random.uniform(3, 5))  # Wait to avoid detection
        try:
            # ✅ Wait until the business listings load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        except:
            print("⚠️ No business listings found!")
            break

        # ✅ Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        businesses = soup.select("div.result")
        
        print("Businesses:", page_count, len(businesses))

        # ✅ Extract business details
        for business in businesses:
            name_tag = business.select_one("a.business-name span")
            phone_tag = business.select_one("div.phones")
            link_tag = business.select_one("a.business-name")
            website_tag = business.select_one("a.track-visit-website")
            location_tag = business.select_one("div.locality")

            name = name_tag.text.strip() if name_tag else "N/A"
            phone = phone_tag.text.strip() if phone_tag else "N/A"
            link = f"https://www.yellowpages.com{link_tag['href']}" if link_tag else "N/A"
            website = website_tag["href"] if website_tag else "N/A"
            location = location_tag.text.strip() if location_tag else "N/A"

            data.append({"Name": name, "Phone": phone, "Link": link, "Website": website, "Location": location})

        # ✅ Check if there is a next page
        next_page = soup.select_one("a.next")
        print("Pagination:", next_page)
        if not next_page:
            break 

        page_count += 1

    return data

# ✅ Save to CSV
def save_to_csv(data, filename="yellowpages_data.csv"):
    if not data:
        print("⚠️ No data to save.")
        return

    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Data saved to {filename}")

# ✅ Run the Scraper
search_term = "Gym"
location = "Florida"
scraped_data = scrape_yellowpages(search_term, location)

if scraped_data:
    save_to_csv(scraped_data)

# ✅ Close the driver
driver.quit()
print("✅ Scraping complete!")