import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime

import pandas as pd

# Get current datetime and format it as YYYY-MM-DD
current_date = datetime.now().strftime("%Y-%m-%d")
print(current_date)

# loading .env
load_dotenv()

crypto_list = ["bitcoin", "ethereum", "dogecoin"]

df = pd.DataFrame(
    columns=[
        "timestamp",
        "batch_id",
        "crypto_id",
        "currency",
        "current_price",
        "market_cap",
        "total_volume",
    ]
)
data_list = []
for crypto in crypto_list:
    url = f"https://api.coingecko.com/api/v3/coins/{crypto}/history?date={current_date}&localization=true"

    # .env variables and api parameters
    # url = "https://api.coingecko.com/api/v3/coins/bitcoin/history?date=2026-01-22&localization=true"
    # url = f"https://api.coingecko.com/api/v3/coins/{crypto_list}/history?date={current_date}&localization=true"
    api_key = os.getenv("COINGECKO_API_KEY")

    headers = {"x-cg-api-key": "{api_key}"}

    # calling api
    response = requests.get(url, headers=headers)

    data = response.json()

    df_tmp = pd.DataFrame()

    df_tmp["current_price"] = [
        value for value in data["market_data"]["current_price"].values()
    ]
    df_tmp["market_cap"] = [
        value for value in data["market_data"]["market_cap"].values()
    ]
    df_tmp["total_volume"] = [
        value for value in data["market_data"]["total_volume"].values()
    ]
    df_tmp["currency"] = [
        value for value in data["market_data"]["current_price"].keys()
    ]
    df_tmp["batch_id"] = "7AM"  # PLACEHOLDER: change to proper batch id: 7AM or 7PM
    df_tmp["crypto_id"] = data["id"]
    df_tmp["timestamp"] = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    df = pd.concat([df, df_tmp], ignore_index=True)

df.to_csv(f"crypto_data_{current_date}_BATCH_7am.csv", index=False)
df.to_json(f"crypto_data_{current_date}_7am.ndjson", orient="records", lines=True)

# # turn json into ndjson
# ndjson_line = json.dumps(data, ensure_ascii=False)

# # Save as .ndjson
# with open(f"bitcoin_data_{current_date}.ndjson", "w", encoding="utf-8") as f:
#     f.write(ndjson_line + "\n")

# print("Conversion complete: bitcoin_data.ndjson created.")
