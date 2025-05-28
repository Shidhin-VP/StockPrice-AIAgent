from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_aws import ChatBedrockConverse
from langchain.tools import tool
import yfinance as yf
import traceback
import json
from datetime import datetime

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
    
@tool(description="Fetches the Stock Price of a company/ticker the user requests for a period of time FROM and TO. If the user does not give an interval, use '1d' as default.")
def Retrieve_historical_stock_price(ticker: str, start: str, end: str, interval: str = "1d") -> str:
    """
    Fetch historical stock prices for a given ticker symbol between a date range. If the user is asking for a period of time, give all the values don't stop if they ask for 1 year also give the entire values fully in a well structured manner, like tables.
    
    Parameters:
    - ticker (str): Ticker symbol (e.g., 'AAPL')
    - start (str): Start date in 'YYYY-MM-DD' format
    - end (str): End date in 'YYYY-MM-DD' format
    - interval (str): Data interval (default is '1d'). Valid intervals: 1m, 2m, 5m, 15m, 1d, 1wk, 1mo
    
    Returns:
    - str: Summary of historical prices
    """
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(start=start, end=end, interval=interval)

        if hist.empty:
            return f"No historical data found for {ticker.upper()} from {start} to {end} with interval '{interval}'."

        # Format the first few rows as a string
        hist_reset = hist.reset_index()
        hist_str = hist_reset[["Date", "Open", "High", "Low", "Close"]].head(5).to_string(index=False)
        #return f"Historical prices for {ticker.upper()} from {start} to {end} (interval: {interval}):\n{hist_str}"
        return hist_str
    except Exception as e:
        return f"Error fetching historical stock data for {ticker.upper()}: {str(e)}"

    
@tool(description="Tool which will return real tie datetime")
def get_current_datetime()->str:
    """
    Get the current date and time in a human-readable format.
    """

    now=datetime.now()
    return now

llm=ChatBedrockConverse(
    #model="us.meta.llama4-scout-17b-instruct-v1:0",
    model="us.amazon.nova-premier-v1:0",
    region_name="us-east-1",
    temperature=0.7
)

agent=create_react_agent(
    model=llm,
    tools=[retrieve_realtime_stock_price,Retrieve_historical_stock_price,get_current_datetime],
    prompt="You are a AI Assistant that will give user the Real-Time and Historical Stock Prices of Companies/Tickers as per user needs, You will only response in plain English and Human Understandable Format and in Times New Roman Font if possible, keep the font human understandable. Also Warn Them as this is about price saying (IMPORTANT) **You are just a help but the user needs to understand and research before any purchace or financial process**"
)

def lambda_handler(event,context):
    try:
        body=json.loads(event['body'])
        prompt=body.get('prompt')
        print("Prompt: ",prompt)
        result=agent.invoke({"messages":[{"role":"user","content":prompt}]})
        if hasattr(result, '__iter__') and not isinstance(result, dict):
            for chunk in result:
                if chunk:
                    final_answer += chunk
        else:
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