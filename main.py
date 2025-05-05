import time
import random
import csv
import requests
import io
import nodriver as uc
from nodriver import ChromeOptions

# User agents for different types of browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/110.0 Safari/537.36",
]

# URL for the raw CSV file hosted on GitHub
csv_url = "https://raw.githubusercontent.com/bugignore/Playwright_Auto/main/Search_data.csv"

def read_csv(url):
    """Fetch and read CSV data from a given URL."""
    response = requests.get(url)
    if response.status_code == 200:
        # Convert the raw CSV data into a file-like object
        csv_file = io.StringIO(response.text)
        
        # Read the CSV content using the csv module
        csv_reader = csv.DictReader(csv_file)
        return list(csv_reader)
    else:
        print(f"❌ Failed to retrieve the CSV file, status code: {response.status_code}")
        return []

def scroll_page(driver, direction="down", loops=10):
    """Scroll the page."""
    for _ in range(loops):
        delta = random.randint(200, 350) * (1 if direction == "down" else -1)
        driver.execute_script(f"window.scrollBy(0, {delta});")
        time.sleep(random.uniform(0.7, 1.2))

def match_and_click_target_text(driver, target_text):
    """Search and click on the target text."""
    print(f"🔍 Looking for text: {target_text}")
    try:
        elements = driver.find_elements_by_xpath(f"//*[text()='{target_text}']")
        if elements:
            element = elements[0]
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(1)
            element.click()
            print(f"🟢 Clicked on matched text: {target_text}")
            return True
    except Exception as e:
        print(f"⚠️ Failed to click '{target_text}': {e}")
    return False

def launch_browser(data_entry):
    """Launch the browser and perform actions."""
    # Set up options to launch Chrome using nodriver
    options = ChromeOptions()
    options.add_argument("--headless")  # Running headless browser
    
    driver = uc.Chrome(options=options, user_agent=random.choice(USER_AGENTS))
    
    keyword = data_entry["search_keyword"]
    target_url = data_entry["target_url"]
    nav_texts = data_entry["nav_texts"]
    texts_by_page = data_entry["texts_by_page"]

    selected_texts = {
        page_name: random.choice([t for t in texts if t.strip()]) if texts else None
        for page_name, texts in texts_by_page.items()
    }
    print(f"\n🎯 Texts selected for this run: {selected_texts}")

    print(f"\n🔍 Searching for: {keyword}")
    driver.get("https://www.google.com")
    time.sleep(random.uniform(3, 5))
    search_box = driver.find_element_by_name("q")
    search_box.send_keys(keyword)
    search_box.submit()
    time.sleep(random.uniform(3, 5))

    # Go through the results and click on the target URL
    for link in driver.find_elements_by_xpath("//a"):
        try:
            href = link.get_attribute("href")
            if href and target_url in href:
                print(f"✅ Found result: {href}")
                link.click()
                break
        except:
            continue

    time.sleep(3)
    scroll_page(driver, "down", loops=6)
    
    if selected_texts.get("Home"):
        if match_and_click_target_text(driver, selected_texts["Home"]):
            scroll_page(driver, "down", loops=6)
            scroll_page(driver, "up", loops=5)

    for header in random.sample(nav_texts, k=min(3, len(nav_texts))):
        try:
            print(f"\n🔗 Navigating to header: {header}")
            driver.find_element_by_xpath(f"//a[text()='{header}']").click()
            time.sleep(random.uniform(3, 5))
            scroll_page(driver, "down", loops=6)
            if selected_texts.get(header):
                match_and_click_target_text(driver, selected_texts[header])
        except Exception as e:
            print(f"⚠️ Could not visit {header}: {e}")

    print("\n✅ Run completed successfully!\n")
    driver.quit()

def main():
    data = read_csv(csv_url)
    for entry in data:
        launch_browser(entry)

if __name__ == "__main__":
    main()
