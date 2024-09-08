# -*- coding: utf-8 -*-
import requests
from datetime import datetime

class Stock:
    def __init__(self, ticker, api_key):
        """
        Initialize a Stock object.
        :param ticker: Ticker symbol of the stock (e.g., 'AAPL').
        :param api_key: RapidAPI key.
        """
        self.ticker = ticker
        self.api_key = api_key

    def _date_to_timestamp(self, date):
        """
        Convert a date in 'YYYY-MM-DD' format to a timestamp.
        :param date: The date in 'YYYY-MM-DD' format.
        :return: Timestamp corresponding to the date.
        """
        return int(datetime.strptime(date, '%Y-%m-%d').timestamp())

    def get_prices_between(self, start_date, end_date):
        """
        Fetch the stock prices between two dates using Yahoo Finance API via RapidAPI.
        :param start_date: The start date in 'YYYY-MM-DD' format.
        :param end_date: The end date in 'YYYY-MM-DD' format.
        :return: List of tuples (date, close price) for the available data between the two dates.
        """
        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-historical-data"
        querystring = {
            "symbol": self.ticker,
            "period1": self._date_to_timestamp(start_date),
            "period2": self._date_to_timestamp(end_date),
            "region": "US"
        }

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        # Debug: Print the raw response
        print(f"Raw data for {self.ticker}: {data}")

        prices = []

        # Extract prices
        for item in data['prices']:
            if 'date' in item and 'close' in item:
                item_date = datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d')
                prices.append((item_date, item['close']))

        if not prices:
            raise ValueError(f"No valid data available for {self.ticker} between {start_date} and {end_date}.")

        return prices

class Portfolio:
    def __init__(self):
        """
        Initialize a Portfolio object.
        """
        self.stocks = []

    def add_stock(self, stock):
        """
        Add a stock to the portfolio.
        :param stock: A Stock object.
        """
        self.stocks.append(stock)

    def profit(self, start_date, end_date):
        """
        Calculate the total profit of the portfolio between two dates.
        :param start_date: The start date in 'YYYY-MM-DD' format.
        :param end_date: The end date in 'YYYY-MM-DD' format.
        :return: The profit of the portfolio between the two dates.
        """
        start_total = 0
        end_total = 0

        # Iterate over each stock in the portfolio
        for stock in self.stocks:
            try:
                # Fetch all prices between the two dates
                prices = stock.get_prices_between(start_date, end_date)
                # Sort prices by date
                prices.sort()

                # Use the first available price (start) and the last available price (end)
                start_price = prices[0][1]  # First price
                end_price = prices[-1][1]   # Last price

                # Accumulate the total value of the portfolio at both dates
                start_total += start_price
                end_total += end_price

            except ValueError as e:
                print(f"Error fetching data for {stock.ticker}: {e}")

        # Calculate the profit
        profit = end_total - start_total
        return profit, start_total

    def annualized_return(self, start_date, end_date):
        """
        Calculate the annualized return of the portfolio between two dates.
        :param start_date: The start date in 'YYYY-MM-DD' format.
        :param end_date: The end date in 'YYYY-MM-DD' format.
        :return: The annualized return as a percentage.
        """
        # Get the profit and the total value at the start date
        profit, start_total = self.profit(start_date, end_date)

        # Calculate the number of days between the two dates
        days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days

        # Calculate the annualized return
        annualized_return = ((profit / start_total) + 1) ** (365 / days) - 1
        return annualized_return

def fx_annualized_return(profit, start_total, start_date, end_date):
    """
    Calculate the annualized return of the portfolio between two dates with profit and start_total previously calculated.
    :param start_date: The start date in 'YYYY-MM-DD' format.
    :param end_date: The end date in 'YYYY-MM-DD' format.
    :return: The annualized return as a percentage.
    """

    # Calculate the number of days between the two dates
    days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days

    # Calculate the annualized return
    annualized_return = ((profit / start_total) + 1) ** (365 / days) - 1
    return annualized_return

if __name__ == "__main__":
    api_key = "62b455dff6msha0c8e8e52b02c94p139a73jsn95cacfa5151d" #TODO: Get API KEY from .env file

    # Create Stock objects
    stock_a = Stock("AAPL", api_key)
    stock_b = Stock("MSFT", api_key)

    # Create Portfolio and add stocks
    portfolio = Portfolio()
    portfolio.add_stock(stock_a)
    portfolio.add_stock(stock_b)

    # Dates for profit and annualized return calculations
    start_date = "2024-08-01"
    end_date = "2024-08-29"

    # Calculate profit and annualized return
    try:
        profit, start_total = portfolio.profit(start_date, end_date)
        print(f"Profit between {start_date} and {end_date}: {profit}")
        # annualized_return = portfolio.annualized_return(start_date, end_date)
        annualized_return = fx_annualized_return(profit, start_total, start_date, end_date)
        print(f"Annualized return: {annualized_return:.2%}")
    except ValueError as e:
        print(f"Error: {e}")