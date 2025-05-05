import asyncio
import csv
import random
import requests
from nodriver import connect, Keys

# Google Drive file ID of the public CSV
CSV_FILE_ID = "1AbCdEfGhIjKlMnOpQ1234567890"  # Replace with your actual file ID
CSV_FILENAME = "search_data.csv"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/110.0 Safari/537.36",
]

def download_csv_from_gdrive(file_id, dest_path=CSV_FILENAME):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        response = requests.get(url)
        with open(dest_path, "wb") as f:
            f.write(response.content)
        print("✅ CSV downloaded successfully from Google Drive.")
    except Exception as e:
        print(f"❌ Failed to download CSV: {e}")

def read_csv(file_name=CSV_FILENAME):
    data = []
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append({
                    "search_keyword": row["search_keyword"],
                    "target_url": row["target_url"]
                })
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
    return data

async def run_browser(entry):
    async with connect(headless=False, user_agent=random.choice(USER_AGENTS)) as browser:
        page = await browser.page()

        keyword = entry['search_keyword']
        target_url = entry['target_url']

        print(f"🔍 Searching Google for: {keyword}")
        await page.get("https://www.google.com")
        await page.type("textarea[name='q']", keyword)
        await page.keyboard.press(Keys.ENTER)
        await page.wait_for_load_state("domcontentloaded")

        links = await page.locator("a").all()
        for link in links:
            href = await link.get_attribute("href")
            if href and target_url in href:
                print(f"✅ Found target link: {href}")
                await link.click()
                break

        print("✅ Run complete!")

async def main():
    download_csv_from_gdrive(CSV_FILE_ID)
    entries = read_csv()
    for entry in entries:
        await run_browser(entry)

if __name__ == "__main__":
    asyncio.run(main())
