from dotenv import load_dotenv
from pydantic import BaseModel
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from tools import get_price_data, calculated_rsi
from tools import run_scanner
import re
# from tools import search_tool


load_dotenv()


# ACCOUNT_BALANCE = 10026
# RISK_PERCENT = 1
# ACCOUNT_CURRENCY = "USD"


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
# llm3 = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview")
llm3 = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

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
 