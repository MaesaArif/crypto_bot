import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime

import pandas as pd


# loading .env
load_dotenv()


def process_market_data(data, df):
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

    market_data_df = pd.concat([df, df_tmp], ignore_index=True)

    return market_data_df


def process_community_data(data, df):
    columns = [
        "facebook_likes",
        "reddit_average_posts_48h",
        "reddit_average_comments_48h",
        "reddit_subscribers",
        "reddit_accounts_active_48h",
    ]
    df_tmp = pd.DataFrame()
    for c in columns:
        df_tmp.loc[0, c] = data["community_data"][c]
    df_tmp["batch_id"] = batch_id
    df_tmp["crypto_id"] = data["id"]
    df_tmp["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    community_data_df = pd.concat([df, df_tmp], ignore_index=True)

    return community_data_df


def process_developer_data(data, df):
    columns = [
        "forks",
        "stars",
        "subscribers",
        "total_issues",
        "closed_issues",
        "pull_requests_merged",
        "pull_request_contributors",
        "code_additions_deletions_4_weeks",
        "commit_count_4_weeks",
    ]
    df_tmp = pd.DataFrame()
    for c in columns:
        df_tmp.loc[0, c] = str(data["developer_data"][c])
    df_tmp["batch_id"] = batch_id
    df_tmp["crypto_id"] = data["id"]
    df_tmp["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    developer_data_df = pd.concat([df, df_tmp], ignore_index=True)

    return developer_data_df


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
    community_data_df = pd.DataFrame(
        columns=[
            "timestamp",
            "batch_id",
            "crypto_id",
            "facebook_likes",
            "reddit_average_posts_48h",
            "reddit_average_comments_48h",
            "reddit_subscribers",
            "reddit_accounts_active_48h",
        ]
    )
    developer_data_df = pd.DataFrame(
        columns=[
            "timestamp",
            "batch_id",
            "crypto_id",
            "forks",
            "stars",
            "subscribers",
            "total_issues",
            "closed_issues",
            "pull_requests_merged",
            "pull_request_contributors",
            "code_additions_deletions_4_weeks",
            "commit_count_4_weeks",
        ]
    )
    for crypto in crypto_list:
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/history?date={current_date}&localization=true"
        api_key = os.getenv("COINGECKO_API_KEY")

        headers = {"x-cg-api-key": "{api_key}"}

        # calling api
        response = requests.get(url, headers=headers)

        data = response.json()
        market_data_df = process_market_data(data, market_data_df)
        community_data_df = process_community_data(data, community_data_df)
        developer_data_df = process_developer_data(data, developer_data_df)

    market_data_df.to_json(
        f"output/crypto_data_{current_date}_BATCH_{batch_id}.ndjson",
        orient="records",
        lines=True,
    )

    community_data_df.to_json(
        f"output/community_data_{current_date}_BATCH_{batch_id}.ndjson",
        orient="records",
        lines=True,
    )

    developer_data_df.to_json(
        f"output/developer_data_{current_date}_BATCH_{batch_id}.ndjson",
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
