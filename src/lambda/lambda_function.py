from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_aws import ChatBedrockConverse
from langchain.tools import tool
import yfinance as yf
import traceback
import json

Rstatus=""
Astatus=""

@tool(description="Fetchs the Current and Closest Stock price for a given ticker symbol (eg. AAPL, MSFT), REALTIME Price of the Stock")
def retrieve_realtime_stock_price(ticker:str)->str:
    """
    Fetchs the Current and Closest Stock price for a given ticker symbol (eg. AAPL, MSFT)
    """
    global Rstatus
    try:
        stock=yf.Ticker(ticker.upper())
        price=stock.history(period="1d")["Close"][-1]
        Rstatus=f"The Current Price of {ticker.upper()} is ${price:.2f}"
        return price
    except Exception as e:
        Rstatus=f"Error fetching stock price for {ticker}: {str(e)}"
        return Rstatus
    
@tool(description="Add to Digits given by user")
def add_digits(digit1:str, digit2:str)->str:
    global Astatus
    try:
        Astatus=f"Adding {digit1} and {digit2}"
        return str(int(digit1)+int(digit2))
    except Exception as e:
        Astatus=f"Error Adding {digit1} and {digit2}"
        return Astatus

llm=ChatBedrockConverse(
    #model="us.meta.llama4-scout-17b-instruct-v1:0",
    model="us.amazon.nova-premier-v1:0",
    region_name="us-east-1",
    temperature=0.7
)

# math_assistant=create_react_agent(
#     model=llm,
#     tools=[add_digits],
#     prompt="You find the sum of numbers when user ask",
#     name="math_assistant"
# )

# stock_price_assistant=create_react_agent(
#     model=llm,
#     tools=[retrieve_realtime_stock_price],
#     prompt="You get the real time stock price of user asked Company or tickers ex: Apple (AAPL) Google etc.",
#     name="stock_price_assistant"
# )

# supervisor=create_supervisor(
#     agents=[math_assistant,stock_price_assistant],
#     model=llm,
#     prompt=("You are a AI Assistant who help User with stock price fetching and doing mathematical calculations")
# ).compile()

agent=create_react_agent(
    model=llm,
    tools=[retrieve_realtime_stock_price,add_digits],
    prompt="You are an AI Agent, understand the user question and only answer in plain english on how they want as a human do, and don't give tags like <thinking> etc. Just simple answer for what the user ask even if it's complex"
)

def lambda_handler(event,context):
    try:
        body=json.loads(event['body'])
        prompt=body.get('prompt')
        print("Prompt: ",prompt)
        result=agent.invoke({"messages":[{"role":"user","content":f"When answer dont give any </thinking> just like a human do answer me in plain english as human does with this prompt: {prompt}"}]})
        if hasattr(result, '__iter__') and not isinstance(result, dict):
            for chunk in result:
                if chunk:
                    final_answer += chunk
        else:
            # Non-streaming: extract final message content
            final_answer = result["messages"][-1].content
        return{
            "statusCode":200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body":json.dumps({
                "prompt":prompt,
                "result":str(result),
                "Status":f"Rstatus: {Rstatus}, Astatus: {Astatus}",
                "Testing":"Supervisor Called and Added Deepseek",
                "AI Result":final_answer,
                "Testing":"Honestly Yes"
            })
        }
    except Exception as e:
        return{
            "statusCode":500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body":json.dumps({
                "error":f"Error: {e}",
                "Testing": f"Error Checker {e}",
                "TraceBack": traceback.format_exc(),
                "Status":f"Rstatus: {Rstatus}, Astatus: {Astatus}",
                "Testing":"Supervisor and Deepseek"
            })
        }