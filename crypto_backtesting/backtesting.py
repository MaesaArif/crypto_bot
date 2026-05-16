from datetime import datetime
import numpy as np
import yfinance as yf
import pandas as pd

# import matplotlib.pyplot as plt

# import seaborn as sns

# from utils import upload_file_to_gcs


def process_yf_ticker_data(data, df, ticker, df_columns):
    df_tmp = data.copy()
    # Shift the data in the dataframe by one row
    df_tmp = df_tmp.shift(1)
    # add timestamp and ticker column
    df_tmp["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
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
    return yfinance_df


def train_arima(df):
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
    # model_fit.summary()

    return model_fit


def validation(model_fit, exogenous_features, data):
    # Making Predictions on Test Set
    forecast = [
        model_fit.forecast(exog=data[exogenous_features].iloc[i]).values[0]
        for i in range(len(data))
    ]
    data["Forecast"] = forecast
    rmse = np.sqrt(mean_squared_error(data["Close"], data["Forecast"]))
    return rmse


def main():
    tickers = ["GOOGL", "BTC-USD"]
    datas = yf_ticker_pull(tickers)


if __name__ == "__main__":
    main()
