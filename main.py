from dotenv import load_dotenv
from pydantic import BaseModel
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from tools import get_price_data, calculated_rsi
from tools import extract_values, decide_trade, detect_symbol, get_market_news, extract_pairs_from_news,run_scanner
import re
# from tools import search_tool


load_dotenv()

# ACCOUNT_BALANCE = 10026
# RISK_PERCENT = 1
# ACCOUNT_CURRENCY = "USD"

# class Responsemessage(BaseModel):
#     topic: str
#     summary: str
#     sources: list[str]
#     tools_used: list[str]

class Tradesignal(BaseModel):
    pair: str
    bias: str
    entry: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    confidence: float
    position_size: float = 0
    risk_percent: float = 0
    account_currency: str = ""


# llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
# llm2 = ChatOpenAI()
llm3 = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")
# llm3 = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

parser = PydanticOutputParser(pydantic_object=Tradesignal)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are a forex data assistant.

    Your job:
    - Use tools to get latest PRICE and RSI
    - Return BOTH values clearly

    Rules:
    - DO NOT make trading decisions
    - DO NOT suggest BUY/SELL
    - DO NOT calculate stop loss or take profit

    Output format MUST be:
    PRICE:<value>
    RSI:<value>

    If data is unavailable, return:
    ERROR
    """),
    ("placeholder","{chat_history}"),
    ("human","{query}"),
    ("placeholder","{agent_scratchpad}"),]).partial(format_instructions=parser.get_format_instructions())

tools = [get_price_data, calculated_rsi]
agent = create_tool_calling_agent(
    llm=llm3, 
    tools=tools, 
    prompt=prompt
    )

agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True
    )

# query = input("What is on your mind? ")
run_scanner(agent_executor)

"""news = get_market_news()
pairs = extract_pairs_from_news(news)
print("News -based pairs:", pairs)

for symbol in pairs:
    query = f"Get the latest price and RSI for {symbol}"

raw_response = agent_executor.invoke({"query": query})
# print(raw_response)
output_chunks = raw_response.get("output")
full_text = ""

for chunk in output_chunks:
    if isinstance(chunk, dict) and "text" in chunk:
        full_text += chunk["text"]
    
print("Raw output:\n",full_text)

price, rsi = extract_values(full_text)

if price is None or rsi is None:
    print("Error: Failed to extract price or RSI from the response.")

else:
    symbol = detect_symbol(query)  # Extract symbol dynamically from the query

    trade = decide_trade(price, rsi, symbol)

    if not trade:
        print("No trade today - stay safe!")

    else:
        print("Final Trade:\n", trade)"""

    

# try:
#     output_chunks = raw_response.get("output")
#     if isinstance(output_chunks, list):
#         full_text = ""
#         for chunk in output_chunks:
#             if isinstance(chunk, dict) and "text" in chunk:
#                 full_text += chunk["text"]
#             elif isinstance(chunk, str):
#                 full_text += chunk
#     elif isinstance(output_chunks, str):
#         full_text = output_chunks
#     else:
#         raise ValueError("Unexpected output format")
    
#     cleaned = re.sub(r"```json|```","", full_text).strip()

#     # print("Raw output:\n", cleaned)

#     if "NO TRADE" in cleaned:
#         print("No trade today - stay safe!")

#     else:
#         start = cleaned.find("{")
#         end = cleaned.rfind("}") + 1
#         json_text = cleaned[start:end]

#         print("Extracted JSON:", json_text)

#         structured_response = parser.parse(json_text)
#         # structured_response = parser.parse(raw_response.get("output")[safest tra0]["text"])
#         position_size = calculate_position_size(
#             ACCOUNT_BALANCE,
#             RISK_PERCENT,
#             structured_response.entry,
#             structured_response.stop_loss,
#             structured_response.pair
#             )
#         structured_response.position_size = position_size
#         structured_response.risk_percent = RISK_PERCENT
#         structured_response.account_currency = ACCOUNT_CURRENCY

#         print("\n Final Trade:\n ", structured_response)
            

# except Exception as e:
#     print("Failed to parse response:", e)
    