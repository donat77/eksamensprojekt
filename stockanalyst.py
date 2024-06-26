import requests
import streamlit as st
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

apikey = "PI4JDGIH2W072OKF"
ticker = st.text_input("Ticker")

class StockData:
    def __init__(self, apikey):
        self.apikey = apikey

    def load(self, ticker):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={ticker}&apikey={self.apikey}&datatype=csv"
        return pd.read_csv(url)

class DataVisualizer:
    def __init__(self):
        self.st = st

    def display(self, data, title):
        self.st.write(title)
        self.st.line_chart(data.set_index('timestamp'))

class LinearRegressionModel:
    def __init__(self): 
        self.model = LinearRegression()

    def performRegression(self, data, startDate, forecastDays):
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        startDate = pd.Timestamp(startDate)
        data = data[data["timestamp"] >= startDate]

        x = data["timestamp"].apply(lambda x: x.toordinal())
        y = data["adjusted close"]

        self.model.fit(x.values.reshape(-1, 1), y)

        futureTimestamp = [data["timestamp"].max() + timedelta(days=i) for i in range(1, forecastDays + 1)]
        futureX = np.array([timestamp.toordinal() for timestamp in futureTimestamp]).reshape(-1, 1)

        futurePredictedY = self.model.predict(futureX)
        futureData = pd.DataFrame({"timestamp": futureTimestamp, "predicted close": futurePredictedY})

        predictedY = self.model.predict(x.values.reshape(-1, 1))

        data["predicted close"] = predictedY
        data = pd.concat([data, futureData])

        return data

if __name__ == "__main__":
    startDate = st.date_input("Start Date", value=(datetime.now() - timedelta(days=365)).date())
    forecastDays = st.slider("Number of days to forecast in the future", min_value=1, max_value=5000, value=30)

    st.title("Data from Alpha Vantage")

    stockData = StockData(apikey)
    dataVisualizer = DataVisualizer()
    linearRegressionModel = LinearRegressionModel()

    if ticker:
        df = stockData.load(ticker)
        df = linearRegressionModel.performRegression(df, startDate, forecastDays)

        dfVisual = df[['timestamp', 'adjusted close', 'predicted close']]
        dataVisualizer.display(dfVisual, ticker)
