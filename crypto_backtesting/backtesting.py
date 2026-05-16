import warnings

warnings.filterwarnings("ignore")

from datetime import datetime
import numpy as np
import yfinance as yf
import pandas as pd
import sys
import os
from pathlib import Path
import statsmodels.api as sm
from sklearn.metrics import root_mean_squared_error

# Add project root to sys.path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

# import matplotlib.pyplot as plt

# import seaborn as sns

from utils.gcs import upload_file_to_gcs


def process_yf_ticker_data(data, df, ticker, df_columns):
    df_tmp = data.copy()
    # Shift the data in the dataframe by one row
    df_tmp = df_tmp.shift(1)
    # add timestamp and ticker column
    df_tmp = df_tmp.reset_index(names="timestamp")
    df_tmp["timestamp"] = df_tmp["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    df_tmp["ticker"] = ticker
    # Select the columns
    df_tmp = df_tmp[df_columns].iloc[2:]

    final_data_df = pd.concat([df, df_tmp], ignore_index=True)

    return final_data_df


def yf_ticker_pull(tickers):
    yfinance_df_columns = ["timestamp", "ticker", "Open", "High", "Low", "Close"]
    yfinance_df = pd.DataFrame(columns=yfinance_df_columns)
    for ticker in tickers:
        current_date = datetime.now().strftime("%Y-%m-%d")
        data = yf.Ticker(ticker)
        # create a variable called 'data_hist' and assigns it to the history method of the Google Ticker object, set to the 'max' period
        data = data.history(period="max")
        # Data cleaning
        yfinance_df = process_yf_ticker_data(
            data, yfinance_df, ticker, yfinance_df_columns
        )

    yfinance_df_PATH = f"output/yfinance_data_{current_date}.ndjson"
    yfinance_df.to_json(
        yfinance_df_PATH,
        orient="records",
        lines=True,
    )
    return yfinance_df, yfinance_df_PATH


def train_arima(df):
    # Ensure columns are numeric to avoid "Pandas data cast to numpy dtype of object" error
    numeric_cols = ["Open", "High", "Low", "Close"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    # pre-process GOOGL
    year_split = 2020
    train = df[df.index.year < year_split]
    test = df[df.index.year >= year_split]

    exogenous_features = ["Open", "High", "Low"]
    train = train[train.columns[:4]]
    test = test[test.columns[:4]]

    # Train ARIMA
    model = sm.tsa.arima.ARIMA(
        endog=train["Close"], exog=train[exogenous_features], order=(1, 1, 1)
    )  # (p,d,q)
    model_fit = model.fit()
    print(model_fit.summary())

    return model_fit, exogenous_features, train, test


def validation(model_fit, exogenous_features, data):
    # Making Predictions on Test Set
    forecast = [
        model_fit.forecast(exog=data[exogenous_features].iloc[i]).values[0]
        for i in range(len(data))
    ]
    data["Forecast"] = forecast
    rmse = root_mean_squared_error(data["Close"], data["Forecast"])
    print(rmse)


def main():
    tickers = ["GOOGL", "BTC-USD"]
    datas, yfinance_df_PATH = yf_ticker_pull(tickers)

    # # upload ndjson to gcs
    # try:
    #     credentials_path = "secret/discord-bot-484904-2dc07a5b046e.json"  # NOTE: hardcoded credential, use more secure method before production
    #     # create new folder each day
    #     gcs_uri = "gs://historical_price_prediction/historical/"
    #     upload_file_to_gcs(yfinance_df_PATH, gcs_uri, credentials_path)
    # except Exception as e:
    #     print("error when uploading ndjson to GCS")
    #     print(e)

    # TODO: Pull training data from BigQ

    # ARIMA Training and Validation, temporarily using datas, later use query from BigQ
    google_df = datas[datas["ticker"] == "GOOGL"]
    google_df = google_df[["timestamp", "Open", "High", "Low", "Close"]].iloc[:]
    google_df["timestamp"] = pd.to_datetime(google_df["timestamp"])
    google_df.set_index("timestamp", inplace=True)
    model_fit, exogenous_features, _, test = train_arima(google_df)
    validation(model_fit, exogenous_features, test)


if __name__ == "__main__":
    main()
