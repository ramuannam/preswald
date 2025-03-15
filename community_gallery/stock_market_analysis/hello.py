# Import necessary libraries
import logging
from preswald import connect, text, table, selectbox, plotly, slider
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Step 1: Establish Connection
try:
    from preswald.engine.service import PreswaldService
    logging.info("Initializing Preswald Service...")
    PreswaldService.initialize()  # Initialize the server
    logging.info("Preswald Service initialized successfully!")
except Exception as e:
    logging.error(f"Failed to initialize Preswald Service: {e}")

# Step 2: Fetch Real-Time Stock Data
def fetch_stock_data(stock_symbol, period="1mo"):
    logging.info(f"Fetching stock data for {stock_symbol} for period {period}...")
    
    try:
        stock = yf.Ticker(stock_symbol)
        df = stock.history(period=period)

        if df.empty:
            raise ValueError("No data fetched, possible API issue")

        df.reset_index(inplace=True)
        df["Date"] = df["Date"].astype(str)  # Convert datetime to string
        logging.info(f"Successfully fetched {len(df)} records for {stock_symbol}.")
        return df

    except Exception as e:
        logging.error(f"Error fetching data for {stock_symbol}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame to prevent crashes

# Step 3: UI Components for User Interaction
try:
    text("# 📈 Interactive Stock Market Analysis")
    logging.info("UI: Title displayed")

    # Select Stock Symbol
    stocks = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN"]
    selected_stock = selectbox("Choose a stock", options=stocks, default="AAPL")
    logging.info(f"User selected stock: {selected_stock}")

    # Select Time Period
    time_options = ["1mo", "3mo", "6mo", "1y"]
    selected_time = selectbox("Select Time Range", options=time_options, default="1mo")
    logging.info(f"User selected time period: {selected_time}")
except Exception as e:
    logging.error(f"Error in UI selection: {e}")

# Step 4: Load and Display Stock Data
df = fetch_stock_data(selected_stock, selected_time)

if not df.empty:
    logging.info("Displaying stock data table...")
    text(f"### 📊 Stock Data for {selected_stock} ({selected_time})")
    table(df[["Date", "Open", "High", "Low", "Close", "Volume"]], title="Stock Market Data")

    # Step 5: Candlestick Chart for Stock Prices
    try:
        text("## 🕯️ Stock Price Candlestick Chart")
        fig_candle = go.Figure(data=[go.Candlestick(x=df["Date"], 
                                                    open=df["Open"], 
                                                    high=df["High"],
                                                    low=df["Low"],
                                                    close=df["Close"])])
        fig_candle.update_layout(title=f"{selected_stock} Candlestick Chart")
        plotly(fig_candle)
        logging.info("Candlestick chart displayed successfully!")
    except Exception as e:
        logging.error(f"Error displaying candlestick chart: {e}")

    # Step 6: Moving Averages for Trend Analysis
    try:
        df["MA7"] = df["Close"].rolling(window=7).mean()
        df["MA30"] = df["Close"].rolling(window=30).mean()
        logging.info("Moving averages calculated successfully!")

        text("## 📊 Moving Averages (7-day & 30-day)")
        fig_ma = px.line(df, x="Date", y=["Close", "MA7", "MA30"], title="Stock Price with Moving Averages")
        plotly(fig_ma)
        logging.info("Moving Averages chart displayed successfully!")
    except Exception as e:
        logging.error(f"Error calculating or displaying moving averages: {e}")

    # Step 7: Filter Stocks Based on Price Threshold
    try:
        text("## 🎯 Filter Stocks by Closing Price")
        threshold = slider("Price Threshold", min_val=100, max_val=1000, default=500)
        logging.info(f"User selected price threshold: {threshold}")

        # Filtered Data
        filtered_df = df[df["Close"] > threshold]
        table(filtered_df[["Date", "Close"]], title="Filtered Stock Data")
        logging.info(f"Filtered {len(filtered_df)} records above {threshold} price.")
    except Exception as e:
        logging.error(f"Error filtering stocks: {e}")

else:
    text("⚠️ No stock data available. Please try again later.")
    logging.warning("No stock data available!")

logging.info("Script execution completed!")
