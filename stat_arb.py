import robin_stocks as r
import alpaca_trade_api as tradeapi
import credentials

# Connect to Alpaca
api_key = "AKSQ2LXNSGAPUIM08RK7"
end_point = "https://api.alpaca.markets"
secret_key = "LF026rOycUWy9meyDTldcRdzIhFK2ISXUwtkG8ER"
api = tradeapi.REST(api_key, secret_key, end_point, api_version='v2')

# Connect to Robinhood
r.authentication.login(credentials.username, credentials.password)

