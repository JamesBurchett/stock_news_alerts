import os
import requests
from datetime import date, timedelta
from twilio.rest import Client

# Stock details:
STOCK = "TSLA"
COMPANY_NAME = "Tesla"

# API endpoints:

ALPHA_ENDPOINT = "https://www.alphavantage.co/query"
ALPHA_API_KEY = os.environ.get("ALPHA_API_KEY_ENV")

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY_ENV")

TWIL_ENDPOINT_SID = os.environ.get("TWIL_ENDPOINT_SID_ENV")
TWIL_API_KEY = os.environ.get("TWIL_API_KEY_ENV")

today = date.today()
yesterday = today - timedelta(days=1)
prior_day = today - timedelta(days=2)

# API Account Access Parameters

time_series_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": ALPHA_API_KEY

}

news_api_parameters = {
    "qInTitle": COMPANY_NAME,
    "from": yesterday,
    "to": today,
    "language": "en",
    "sortBy": "popularity",
    "pageSize": 3,
    "apiKey": NEWS_API_KEY,

}

#   Alpha vantage get request:

response = requests.get(url=ALPHA_ENDPOINT, params=time_series_parameters)
response.raise_for_status()
price_data = response.json()

# Calculate stock price change % from previous day using data obtained from Alpha vantage:

yesterday_close = float(price_data["Time Series (Daily)"][f"{yesterday}"]["4. close"])
prior_day_close = float(price_data["Time Series (Daily)"][f"{prior_day}"]["4. close"])
percentage_change = round((yesterday_close - prior_day_close) / yesterday_close * 100, 1)

# Calculate if price change is significant and if it is get top 3 recent news stories:
get_news = False

if percentage_change >= 1.00 or percentage_change <= -1.00:  # may have used abs function here to get an absolute value
    get_news = True

if get_news:
    response = requests.get(url=NEWS_ENDPOINT, params=news_api_parameters)
    response.raise_for_status()
    news_data = response.json()["articles"]
    print(news_data)

    for headlines in news_data:
        headline = headlines["title"]
        description = headlines["description"]
        stock_message = f"{STOCK} {percentage_change}%\nHeadline:{headline}\nBrief:{description}"
        print(stock_message)

        # Send message via Twillio:

        client = Client(TWIL_ENDPOINT_SID, TWIL_API_KEY)
        message = client.messages \
            .create(
            body=stock_message,
            from_='+17152604418',
            to='+44 7906 262635'
        )

        print(message.status)

        # TODO schedule in Python anywhere storing the API keys in Environment Variables
        # TODO Update emoji icons to up and down to add to SMS
        # TODO Build GUI interface in order to maintain a portfolio of stocks to get messages about
        # TODO code changes absolute value function (abs) could be used as could list comprehension as > Pythonic