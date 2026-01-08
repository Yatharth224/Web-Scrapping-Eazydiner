import requests
import csv
import os
import time

CITY = "bengaluru" # city as your wish

OUTPUT_FOLDER = "final_restro"
OUTPUT_FILENAME = f"luxury_dining_{CITY}.csv"
FULL_PATH = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)

BASE_URL = "https://www.eazydiner.com/_next/data/ZQeUsJi79IVCefxOTEA_u/en/restaurants.json"

cookies = {
    'islive': '0',
    'userLocation': '%7B%22name%22%3A%22Bengaluru%22%2C%22code%22%3A%22bengaluru%22%7D',
}
#cookies are accordign to your cities
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'x-nextjs-data': '1',
}
# headers are according to your city
def extract_restaurants(json_data):
    try:
        items = json_data["pageProps"]["listingData"]["data"]["data"]
    except KeyError:
        return []

    rows = []

    for item in items:
        name = item.get("name", "")
        location = item.get("location", "")
        cost = item.get("cost_for_two", "")

        images = []
        for key in ["image", "gallery", "photos", "album_img", "photo_gallery"]:
            val = item.get(key)
            if isinstance(val, list):
                images.extend(val)
            elif isinstance(val, str):
                images.append(val)

        rows.append({
            "name": name,
            "location": location,
            "cost_for_two": cost,
            "images": list(set(images))
        })

    return rows

all_rows = []
page = 1

while True:
    params = {
        "location": CITY,
        "categories[]": "luxury-dining",
        "page": page
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=headers,
        cookies=cookies
    )

    if response.status_code != 200:
        break

    try:
        json_data = response.json()
    except ValueError:
        break

    rows = extract_restaurants(json_data)

    if not rows:
        break

    all_rows.extend(rows)
    page += 1
    time.sleep(1)

if not all_rows:
    exit()

max_images = max(len(r["images"]) for r in all_rows)

csv_headers = ["name", "location", "cost_for_two"] + [
    f"image{i+1}" for i in range(max_images)
]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

with open(FULL_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)

    for r in all_rows:
        row = [r["name"], r["location"], r["cost_for_two"]]
        row.extend(r["images"])
        row.extend([""] * (max_images - len(r["images"])))
        writer.writerow(row)
