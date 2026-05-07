from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import tool
from datetime import datetime
import time
from colorama import Fore, Style, init
import winsound
import yfinance as yf
import pandas as pd
import re
init(autoreset=True)

search = DuckDuckGoSearchRun()


PAIRS_MAP = {
    "eur": "EURUSD=X",
    "usd": "EURUSD=X",   # fallback mapping
    "gbp": "GBPUSD=X",
    "jpy": "USDJPY=X",
    "inr": "USDINR=X",
}

# @tool
# def duckduckgo_search(query: str) -> str:
#     """Searches the web for information"""
#     return search.run(query)

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

def get_market_news():
    news = search.invoke("forex news USD EUR JPY GBP today")
    return news

def extract_pairs_from_news(news):

    pairs = set()
    news = news.lower()

    for keyword, symbol in PAIRS_MAP.items():
        if keyword in news:
            pairs.add(symbol)
    
    if not pairs:
        pairs.add("EURUSD=X")  # Default pair if no keywords found
    
    return list(pairs)[:3]




    # if "eur" in news:
    #     pairs.append("EURUSD=X")
    # if "gbp" in news:
    #     pairs.append("GBPUSD=X")
    # if "jpy" in news:
    #     pairs.append("USDJPY=X")
    # if "inr" in news:
    #     pairs.append("USDINR=X")

    # return list(set(pairs))

def extract_values(text):
    price_match = re.search(r"PRICE:(\d+\.\d+)", text)
    rsi_match = re.search(r"RSI:(\d+\.\d+)", text)

    price = float(price_match.group(1)) if price_match else None
    rsi = float(rsi_match.group(1)) if rsi_match else None

    return price, rsi

def decide_trade(price, rsi,symbol,atr):
    
    if price is None or rsi is None or atr is None:
        return "💀 NO TRADE, STAY SAFE!"
    
    atr = abs(float(atr))

    if rsi > 60:
        bias = "BUY 🐂"
    elif rsi < 40:
        bias = "SELL 🐻"
    else:
        return " 💀 NO TRADE, STAY SAFE!"
    
    print("ATR:", atr)
    print("PRICE:", price)
    print("BIAS:", bias)
    
    if "JPY" in symbol:
        sl_distance = max(atr * 1.2, 0.10)
    else:
        sl_distance = max(atr * 1.2, 0.0010)

    tp_distance = sl_distance * 2
    
    if bias == "BUY":
        stop_loss = price - sl_distance
        take_profit = price + tp_distance

        if not (stop_loss < price < take_profit):
            return "💀 NO TRADE, STAY SAFE!"

    else:
        stop_loss = price + sl_distance
        take_profit = price - tp_distance

        if not (take_profit < price < stop_loss):
            return "💀 NO TRADE, STAY SAFE!"

    return {
        "pair": symbol,
        "bias": bias,
        "entry": round(price, 5),
        "take_profit": round(take_profit, 5),
        "stop_loss": round(stop_loss, 5),
        "risk_reward": 2,
        "confidence": round(min(abs(rsi - 50) / 50, 1.0), 2)
    }
def detect_symbol(query):
    query = query.lower()

    if "eur" in query and "usd" in query:
        return "EURUSD=X"
    elif "gbp" in query and "usd" in query:
        return "GBPUSD=X"
    elif "usd" in query and "jpy" in query:
        return "USDJPY=X"
    elif "usd" in query and "inr" in query:
        return "USDINR=X"
    else:
        return "EURUSD=X"
    
def analyse_symbol(symbol,agent_executor):
    query = f"Get the latest price and RSI for {symbol}"
    raw_response = agent_executor.invoke({"query": query})
    output_chunks = raw_response.get("output")
    full_text = ""
    for chunk in output_chunks:
        if isinstance(chunk, dict) and "text" in chunk:
            full_text += chunk["text"]
    
    price, rsi = extract_values(full_text)
    data = yf.download(symbol, period="5d", interval="5m")
    atr = calculated_atr(data)
    trade = decide_trade(price, rsi, symbol, atr)

    if not trade:
        print(f"No trade for {symbol} - stay safe!")
        return None
    
    # size = calculate_position_size(10000, 1, trade["entry"], trade["stop_loss"], symbol)
    # trade["position_size"] = size
    # trade["risk_percent"] = RISK_PERCENT
    # trade["account_currency"] = ACCOUNT_CURRENCY
    return trade

def calculated_atr(data, period=14):
    high = data['High']
    low = data['Low']
    close = data['Close']

    # Handle yfinance multi-index columns
    if hasattr(high, "columns"):
        high = high.iloc[:, 0]

    if hasattr(low, "columns"):
        low = low.iloc[:, 0]

    if hasattr(close, "columns"):
        close = close.iloc[:, 0]

    high_low = high - low

    high_close = abs(high - close.shift())

    low_close = abs(low - close.shift())

    true_range = pd.concat([high_low, high_close, low_close],axis=1).max(axis=1)

    atr = true_range.rolling(period).mean()

    latest_atr = atr.iloc[-1]

    return abs(float(latest_atr))
    # hight_low = data['High'] - data['Low']
    # high_close = abs(data['High'] - data['Close'].shift())
    # low_close = abs(data['Low'] - data['Close'].shift())
    # true_range = pd.concat([hight_low, high_close, low_close], axis=1).max(axis=1)
    # atr = true_range.rolling(window=period).mean()
    # return float(atr.iloc[-1])

def send_alert(trade):
    # Placeholder for sending trade alert to Telegram or other platforms
    if not isinstance(trade, dict):
        print("Invalid trade format:", trade)
        return
    
    print("\n🚨 TRADE ALERT 🚨")
    winsound.Beep(1000, 500)  # Beep sound (frequency, duration)
    print(f"Pair: {trade['pair']}")
    print(f"Bias: {trade['bias']}")
    print(f"Entry: {trade['entry']}")
    print(f"Take Profit: {trade['take_profit']}")
    print(f"Stop Loss: {trade['stop_loss']}")
    print(f"Risk/Reward: {trade['risk_reward']}")
    print(f"Confidence: {trade['confidence']}")
    print("Stay safe and trade wisely!")


def run_scanner(agent_executor):
    while True:
        print("\n🔍 Fetching news...")
        news = get_market_news()
        print("=" * 50)
        print(Fore.LIGHTRED_EX + "Latest news:\n", Fore.BLUE+ news)
        print("=" * 50)
        pairs = extract_pairs_from_news(news)
        print("News-based pairs:", pairs)

        for symbol in pairs:
            trade = analyse_symbol(symbol, agent_executor)
            if trade:
                send_alert(trade)
            else:
                print(f"No trade for {symbol} - stay safe!")

        print("Waiting for the next scan...")
        time.sleep(120)  # Wait for 2 minutes before the next scan

# def calculate_position_size(account_balance, risk_percent, entry, stop_loss,pair):
#     risk_amount = account_balance * (risk_percent / 100)
#     if "JPY" in pair:
#         pip_size = 0.01
#     else:
#         pip_size = 0.0001
    
#     stop_loss_pips = abs(entry - stop_loss) / pip_size

#     if stop_loss_pips == 0:
#         return 0  # Avoid division by zero
    
#     pip_value_per_lot = 10  # Standard pip value for a lot

#     position_size = risk_amount / (stop_loss_pips * pip_value_per_lot)
#     return round(position_size, 4)