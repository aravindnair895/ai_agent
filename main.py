from dotenv import load_dotenv
from pydantic import BaseModel
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from tools import duckduckgo_search, get_price_data, calculated_rsi 
import re
# from tools import search_tool

def calculate_position_size(account_balance, risk_percent, entry, stop_loss,pair):
    risk_amount = account_balance * (risk_percent / 100)
    if "JPY" in pair:
        pip_size = 0.01
    else:
        pip_size = 0.0001
    
    stop_loss_pips = abs(entry - stop_loss) / pip_size

    if stop_loss_pips == 0:
        return 0  # Avoid division by zero
    
    pip_value_per_lot = 10  # Standard pip value for a lot

    position_size = risk_amount / (stop_loss_pips * pip_value_per_lot)
    return round(position_size, 4)

load_dotenv()

ACCOUNT_BALANCE = 10026
RISK_PERCENT = 1
ACCOUNT_CURRENCY = "USD"

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
    You are a professional forex trading assistant.

    Use tools (price + RSI) to analyze market.

    Rules:
    - RSI > 60 → BUY
    - RSI < 40 → SELL
    - Otherwise → NO TRADE
    - Risk reward must be >= 1.5
     
     If user explicitly asks for relaxed conditions,
    you may use:
    - RSI > 55 → BUY
    - RSI < 45 → SELL

    If there is NO TRADE, return exactly:
    NO TRADE

    If there is a valid trade, return ONLY JSON:
    {{
    "pair": "...",
    "bias": "BUY or SELL",
    "entry": float,
    "stop_loss": float,
    "take_profit": float,
    "risk_reward": float,
    "confidence": float
    }}
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

query = input("What is on your mind? ")
raw_response = agent_executor.invoke({"query": query})
# print(raw_response)

try:
    output_chunks = raw_response.get("output")
    if isinstance(output_chunks, list):
        full_text = ""
        for chunk in output_chunks:
            if isinstance(chunk, dict) and "text" in chunk:
                full_text += chunk["text"]
            elif isinstance(chunk, str):
                full_text += chunk
    elif isinstance(output_chunks, str):
        full_text = output_chunks
    else:
        raise ValueError("Unexpected output format")
    
    cleaned = re.sub(r"```json|```","", full_text).strip()

    # print("Raw output:\n", cleaned)

    if "NO TRADE" in cleaned:
        print("No trade today - stay safe!")

    else:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        json_text = cleaned[start:end]

        print("Extracted JSON:", json_text)

        structured_response = parser.parse(json_text)
        # structured_response = parser.parse(raw_response.get("output")[safest tra0]["text"])
        position_size = calculate_position_size(
            ACCOUNT_BALANCE,
            RISK_PERCENT,
            structured_response.entry,
            structured_response.stop_loss,
            structured_response.pair
            )
        structured_response.position_size = position_size
        structured_response.risk_percent = RISK_PERCENT
        structured_response.account_currency = ACCOUNT_CURRENCY

        print("\n Final Trade:\n ", structured_response)
            

except Exception as e:
    print("Failed to parse response:", e)
    
# response = llm3.invoke("what is the meaning of life?")
# print(response.content)