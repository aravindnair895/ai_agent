from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import tool
from datetime import datetime
import yfinance as yf
import pandas as pd

search = DuckDuckGoSearchRun()

@tool
def duckduckgo_search(query: str) -> str:
    """Searches the web for information"""
    return search.run(query)

# search_tool = tool(
#     name="duckduckgo_search",
#     description="Searches the web for information",
#     func=search.run
# )

@tool
def get_price_data(symbol: str) -> str:
    """Get latest price data of a forex pair like EURUSD=X"""
    data = yf.download(symbol, period="5d", interval="5m")
    return data.tail(1).to_string()

@tool
def calculated_rsi(symbol: str) -> str:
    """Calculate the Relative Strength Index (RSI) for a forex pair"""
    data = yf.download(symbol, period="5d", interval="5m")
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]
    if hasattr(latest_rsi, 'values'):
        latest_rsi = latest_rsi.values[0]  # Convert to native Python float if it's a numpy type
    return f"The latest RSI for {symbol} is {latest_rsi:.2f}"