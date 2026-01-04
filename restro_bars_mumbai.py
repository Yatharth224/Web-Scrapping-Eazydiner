import requests
import csv
import os
import time

CITY = "mumbai"         
CATEGORY = "bar-pub"

OUTPUT_FOLDER = "final_restro"
OUTPUT_FILENAME = f"restro_bar_{CITY}_data_.csv"
FULL_PATH = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


cookies = {
    'islive': '0',
    'userLocation': '%7B%22name%22%3A%22Delhi%20NCR%22%2C%22code%22%3A%22delhi-ncr%22%7D',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'referer': f'https://www.eazydiner.com/restaurants?location={CITY}',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'x-nextjs-data': '1',
}

BASE_URL = "https://www.eazydiner.com/_next/data/ZQeUsJi79IVCefxOTEA_u/en/restaurants.json"

def extract_restaurants(json_data):
    try:
        items = json_data["pageProps"]["listingData"]["data"]["data"]
    except:
        return []

    output = []

    for item in items:
        name = item.get("name", "") or ""
        location = item.get("location", "") or ""
        cost = item.get("cost_for_two", "") or ""

        images = []
        for key in ["image", "gallery", "photos", "album_img", "photo_gallery"]:
            value = item.get(key)
            if value:
                if isinstance(value, list):
                    images.extend(value)
                elif isinstance(value, str):
                    images.append(value)

        images = list(dict.fromkeys(images))  # remove duplicates

        output.append({
            "name": name,
            "location": location,
            "cost_for_two": cost,
            "images": images
        })

    return output


all_rows = []
page = 1

print(f"\n Scraping {CITY.upper()} Bars (NO DATE FILTER)\n")

while True:
    print(f"Fetching page {page}...")

    params = {
        "location": CITY,
        "categories[]": CATEGORY,
        "page": page
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=headers,
        cookies=cookies
    )

    print("Status Code:", response.status_code)

    if response.status_code != 200:
        print("❌ Request failed. Stopping.")
        break

    rows = extract_restaurants(response.json())
    if not rows:
        print("No more data.")
        break

    all_rows.extend(rows)
    page += 1
    time.sleep(1)

max_images = max((len(r["images"]) for r in all_rows), default=0)

csv_headers = ["name", "location", "cost_for_two"] + [
    f"image{i+1}" for i in range(max_images)
]

with open(FULL_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)

    for r in all_rows:
        row = [r["name"], r["location"], r["cost_for_two"]]
        row.extend(r["images"])
        row.extend([""] * (max_images - len(r["images"])))
        writer.writerow(row)

print("DONE SUCCESSFULLY!")
print(f"Total Restaurants: {len(all_rows)}")
print(f"CSV Saved → {FULL_PATH}")