import requests
import json
from dotenv import load_dotenv
import os

# loading .env
load_dotenv()

# .env variables and api parameters
url = "https://api.coingecko.com/api/v3/coins/bitcoin/history?date=2026-01-22&localization=true"
api_key = os.getenv('COINGECKO_API_KEY')


headers = {"x-cg-api-key": "{api_key}"}

# calling api
response = requests.get(url, headers=headers)

data = response.json()

# turn json into ndjson
ndjson_line = json.dumps(data, ensure_ascii = False)

# Save as .ndjson
with open("bitcoin_data.ndjson", "w", encoding="utf-8") as f:
    f.write(ndjson_line + "\n")

print("Conversion complete: bitcoin_data.ndjson created.")