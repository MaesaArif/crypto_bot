import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from utils.gcs import upload_file_to_gcs


def process_yf_ticker_data(data, df, ticker, df_columns, mode="daily"):
    df_tmp = data.copy()
    if mode != "daily":
        # Shift the data in the dataframe by one row
        df_tmp = df_tmp.shift(1)
    # add timestamp and ticker column
    df_tmp = df_tmp.reset_index(names="timestamp")
    df_tmp["timestamp"] = df_tmp["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    df_tmp["ticker"] = ticker
    # Select the columns
    if mode != "daily":
        df_tmp = df_tmp[df_columns].iloc[2:]
    else:
        df_tmp = df_tmp[df_columns].iloc[:]

    final_data_df = pd.concat([df, df_tmp], ignore_index=True)

    return final_data_df


def yf_ticker_pull(tickers, mode):
    yfinance_df_columns = ["timestamp", "ticker", "Open", "High", "Low", "Close"]
    yfinance_df = pd.DataFrame(columns=yfinance_df_columns)
    current_date = datetime.now().strftime("%Y-%m-%d")
    for ticker in tickers:
        data = yf.Ticker(ticker)
        # create a variable called 'data_hist' and assigns it to the history method of the Google Ticker object
        if mode == "daily":
            data = data.history(period="1d")
        elif mode == "historical":
            data = data.history(period="max")
        else:
            raise ValueError("mode is either daily or historical")
        yfinance_df = process_yf_ticker_data(
            data, yfinance_df, ticker, yfinance_df_columns, mode
        )

    yfinance_df_PATH = f"output/yfinance_data_{current_date}_{mode}.ndjson"
    yfinance_df.to_json(
        yfinance_df_PATH,
        orient="records",
        lines=True,
    )
    return yfinance_df, yfinance_df_PATH


if __name__ == "__main__":
    datas, yfinance_df_PATH = yf_ticker_pull(["GOOGL", "BTC-USD"], "daily")
    # upload ndjson to gcs
    try:
        credentials_path = "secret/discord-bot-484904-2dc07a5b046e.json"  # NOTE: hardcoded credential, use more secure method before production
        # create new folder each day
        gcs_uri = "gs://historical_price_prediction/historical/"
        upload_file_to_gcs(yfinance_df_PATH, gcs_uri, credentials_path)
    except Exception as e:
        print("error when uploading ndjson to GCS")
        print(e)
