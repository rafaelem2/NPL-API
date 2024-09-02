from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# WebDriver configuration with ChromeDriverManager
options = Options()
options.headless = True  # Set to True to run headlessly
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Set maximum page load timeout
driver.set_page_load_timeout(60)

# Base URL of the athletes page
base_url = "https://olympics.com/en/paris-2024/athletes/all-disc/brazil"
driver.get(base_url)

# Maximum number of pages to visit
max_pages = 6

# List to store athlete links
athlete_links = []

# Scrape athlete links from paginated pages
for _ in range(max_pages):
    time.sleep(3)
    
    # Attempt to accept cookies, if the button exists
    try:
        accept_cookies_button = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
        accept_cookies_button.click()
    except Exception:
        pass  # Cookies button not found or already accepted
    
    # Select all anchor tags that contain athlete links
    try:
        athlete_link_elements = driver.find_elements(By.CSS_SELECTOR, "a.competitor-container")
        if athlete_link_elements:
            for element in athlete_link_elements:
                href = element.get_attribute('href').strip()
                athlete_links.append(href)
    except Exception:
        pass  # Error capturing athlete page links
    
    # Attempt to click the "Next Page" button
    try:
        next_page_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//button[@aria-label="next page"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_page_button)
        time.sleep(1)  # Wait a moment to ensure the button is visible
        driver.execute_script("arguments[0].click();", next_page_button)
        time.sleep(5)  # Wait a moment for the next page to load
    except Exception:
        break  # Error clicking the next page button or no more pages

# Prepare data for CSV
data_rows = []

# Iterate over each athlete link to extract data
for link in athlete_links:
    driver.get(link)
    time.sleep(3)  # Wait for the page to load
    
    try:
        # Extract data using the specified XPaths
        main_content = driver.find_element(By.XPATH, '//*[@id="PersonInfo"]/div/div/div[2]').text.strip()
        name = driver.find_element(By.XPATH, '//*[@id="PersonInfo"]/div/div/div[2]/div[1]/div[1]/b').text.strip()
        
        bio_medals = driver.find_element(By.XPATH, '//*[@id="BioMedals"]').text.strip()
        biographical_info = driver.find_element(By.XPATH, '//*[@id="BiographicalInformation"]').text.strip()
        milestones = driver.find_element(By.XPATH, '//*[@id="milestones"]').text.strip()
        
        data_rows.append({
            "Name": name,
            "MainContent": main_content,
            "BioMedals": bio_medals,
            "BiographicalInformation": biographical_info,
            "Milestones": milestones
        })
    except Exception:
        # If there's an error, append a row with empty fields
        data_rows.append({
            "Name": "",
            "MainContent": "",
            "BioMedals": "",
            "BiographicalInformation": "",
            "Milestones": ""
        })

# Save data to CSV
csv_file = "athletes_data.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["Name", "MainContent", "BioMedals", "BiographicalInformation", "Milestones"])
    writer.writeheader()
    writer.writerows(data_rows)

# Close the browser
driver.quit()
