import json
import glob
import hashlib
import os
import pandas as pd
from geopy import geocoders
from geopy.geocoders import Nominatim
from serpapi import GoogleSearch


def search_city(city_name):
    geolocator = Nominatim(user_agent="barselector")
    location = geolocator.geocode(city_name)
    return location


def convert_location_to_str(location, zoom=16):
    latitude_str = f"{location.latitude:.6f}"
    longitude_str = f"{location.longitude:.6f}"
    return f"@{latitude_str},{longitude_str},{zoom}z"


def google_search(params):
    # Send the request and get the JSON response
    search = GoogleSearch(params)
    results = search.get_dict()
    found = False
    if "local_results" in results:
        end_results = results["local_results"]
        found = True
    else:
        end_results = results["error"]
    return (found, results, end_results)


def dump_search(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# load the api key from a file
with open("api_key.txt", "r") as file:
    api_key = file.read().strip()

# Set up the query parameters
location = search_city("Delft")
location_str = convert_location_to_str(location, 13)  # specify zoom level
params = {
    "engine": "google_maps",
    "q": "bars in delft",
    "ll": location_str,
    "google_domain": "google.nl",
    "num": "0",
    "start": "0",
    "api_key": api_key,
}


# compute hash for  params dict
hash_params = hashlib.md5(
    json.dumps(params, sort_keys=True).encode("utf-8")
).hexdigest()
os.makedirs(f"data/{hash_params}", exist_ok=True)


num_results = 200
dump_search(f"data/{hash_params}/search_params.json", params)
for k in range(0, num_results, 20):
    print(f"Getting results {k} to {k+20}")
    params["start"] = str(k)
    (found, results, end_results) = google_search(params)
    dump_search(f"data/{hash_params}/all_results_{k:02}.json", results)
    if found:
        dump_search(f"data/{hash_params}/cafes_{k:02}.json", end_results)
    else:
        break


# %% load results and extract data

# list all files matching data/cafes_00.json
files = glob.glob(f"data/{hash_params}/cafes_*.json")


# load the data
cafes = []
for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        # merge cafes and data
        cafes.extend(data)
print(cafes)


# select only usefull keys
keys_to_keep = [
    "title",
    "gps_coordinates",
    "rating",
    "reviews",
    "price",
    "type",
    "types",
    "address",
    "open_state",
    "hours",
    "operating_hours",
    "phone",
    "website",
    "service_options",
]

# create a new list of cafes with only the selected keys
cafes_selected = []
for cafe in cafes:
    cafe_selected = {key: cafe[key] for key in keys_to_keep if key in cafe}
    cafes_selected.append(cafe_selected)


print(cafes_selected)

df = pd.DataFrame(cafes_selected)

# save the dataframe to a csv file
df.to_csv(f"data/{hash_params}/cafes.csv", index=False)
