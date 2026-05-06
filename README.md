# AI Forex Trading Scanner

An automated AI-powered forex market scanner built using Python, LangChain, Gemini, and Yahoo Finance.

The system continuously:
- Fetches forex market news
- Detects relevant currency pairs
- Retrieves live market price data
- Calculates RSI and ATR indicators
- Generates trade signals automatically
- Sends trade alerts in real time

---

# Features

## Automated News-Based Scanning
The bot fetches forex-related news and automatically determines which currency pairs are relevant.

Example:
- EUR news → EUR/USD
- JPY news → USD/JPY

---

## Multi-Pair Forex Analysis
Currently supported:
- EUR/USD
- GBP/USD
- USD/JPY
- USD/INR

The architecture can easily be extended to support more forex pairs.

---

## Technical Indicators

### RSI (Relative Strength Index)
Used for trade direction filtering.

Rules:
- RSI > 60 → BUY
- RSI < 40 → SELL
- Otherwise → NO TRADE

---

### ATR (Average True Range)
Used for dynamic stop loss and take profit calculations based on market volatility.

Benefits:
- Adaptive risk management
- Volatility-aware trades
- More realistic trading behavior

---

## Risk Management

The system currently uses:
- Dynamic ATR-based Stop Loss
- 1:2 Risk-to-Reward Ratio

Example:
- Risk: 10 pips
- Reward: 20 pips

---

# Project Structure

```bash
ai-agent/
│
├── main.py          # Main application runner
├── tools.py         # Trading logic + utilities
├── .env             # API keys
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/aravindnair895/ai_agent.git
cd ai_agent
```

### 2. Create virtual environment

```
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```
OPENAI_API_KEY=your_api_key
GOOGLE_API_KEY=your_api_key
```

---

## ▶️ Run the Project

```
python main.py
```

---

## 📌 Example Use Case

```
Input: "Give me a EUR/USD trade idea"
Output: 
- Bias: Bullish
- Entry: 1.08
- Stop Loss: 1.075
- Take Profit: 1.09
```

---

## 🔒 Security Note

* API keys are stored in `.env` (not committed to Git)
* Never expose your credentials publicly

---

## 🧠 Future Improvements

* Add RAG-based strategy memory
* Backtesting module
* Web dashboard (Streamlit / FastAPI)
* Risk management system
* Multi-asset support

---

## 👨‍💻 Author

Aravind Somanath

---

## ⭐ Contribution

Feel free to fork, improve, and submit pull requests!
