import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime

import pandas as pd


# loading .env
load_dotenv()


def daily_api_call(crypto_list: list, batch_id: str = "7AM"):
    # Get current datetime and format it as YYYY-MM-DD
    current_date = datetime.now().strftime("%Y-%m-%d")

    market_data_df = pd.DataFrame(
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
    for crypto in crypto_list:
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/history?date={current_date}&localization=true"
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
        df_tmp["batch_id"] = batch_id
        df_tmp["crypto_id"] = data["id"]
        df_tmp["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        market_data_df = pd.concat([market_data_df, df_tmp], ignore_index=True)

    market_data_df.to_csv(
        f"output/crypto_data_{current_date}_BATCH_{batch_id}.csv", index=False
    )
    market_data_df.to_json(
        f"output/crypto_data_{current_date}_BATCH_{batch_id}.ndjson",
        orient="records",
        lines=True,
    )


if __name__ == "__main__":
    crypto_list = ["bitcoin", "ethereum", "dogecoin"]
    batch_id = "7AM"
    daily_api_call(crypto_list, batch_id)


# # turn json into ndjson
# ndjson_line = json.dumps(data, ensure_ascii=False)

# # Save as .ndjson
# with open(f"bitcoin_data_{current_date}.ndjson", "w", encoding="utf-8") as f:
#     f.write(ndjson_line + "\n")

# print("Conversion complete: bitcoin_data.ndjson created.")
