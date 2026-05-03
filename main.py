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


load_dotenv()

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


# llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
# llm2 = ChatOpenAI()
llm3 = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

parser = PydanticOutputParser(pydantic_object=Tradesignal)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a forex trading assistant.

    Use tools to analyze market data.

    Rules:
    - Always provide structured output
    - Include entry, stop_loss, take_profit
    - Risk reward must be >= 1.5
    - If unsure, return "NO TRADE"
      \n{format_instructions}""",),
    ("placeholder","{chat_history}"),
    ("human","{query}"),
    ("placeholder","{agent_scratchpad}"),]).partial(format_instructions=parser.get_format_instructions())

tools = [duckduckgo_search, get_price_data, calculated_rsi]
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
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    json_text = cleaned[start:end]

    print("Extracted JSON:", json_text)

    if "NO TRADE" in cleaned:
        print("No trade today - stay safe!")
    else:
        structured_response = parser.parse(json_text)
        # structured_response = parser.parse(raw_response.get("output")[0]["text"])
        print(structured_response)
            

except Exception as e:
    print("Failed to parse response:", e)
    
# response = llm3.invoke("what is the meaning of life?")
# print(response.content)