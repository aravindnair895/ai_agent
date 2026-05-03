# 🤖 AI Trading Agent

An AI-powered trading assistant that analyzes market data and generates trade ideas (e.g., EUR/USD) using automated tools and LLM-based reasoning.

---

## 🚀 Features

* 📊 Fetches real-time or historical market data
* 🧠 Analyzes trends and patterns
* 💡 Generates trade ideas (buy/sell, entry, SL/TP)
* 🔧 Modular tool-based architecture
* ⚡ Built for extensibility (RAG, strategies, etc.)

---

## 🛠️ Tech Stack

* Python
* LangChain (or your agent framework)
* yfinance
* dotenv (for secure API key handling)

---

## 📁 Project Structure

```
ai_agent/
├── main.py              # Entry point
├── tools.py             # Custom tools (data fetching, analysis)
├── requirements.txt     # Dependencies
├── .env                 # secret data (API keys)
├── .gitignore
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
