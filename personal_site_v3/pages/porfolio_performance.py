import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")

# Predefined list of popular tickers with their full company names
def get_ticker_list():
    # URLs of the Yahoo Finance pages
    urls = {
        'Stocks': 'https://finance.yahoo.com/most-active',
        'ETFs': 'https://finance.yahoo.com/etfs',
        'Crypto': 'https://finance.yahoo.com/cryptocurrencies'
    }

    # Initialize an empty list to store DataFrames
    dfs = []

    # Loop through each URL and scrape the table
    for category, url in urls.items():
        # Send a GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table containing the data
        table = soup.find('table')
        
        # Extract table headers
        headers = [th.text.strip() for th in table.find_all('th')]
        
        # Extract table rows
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cells = row.find_all('td')
            if len(cells) > 1:  # Ensure the row contains data
                rows.append([cell.text.strip() for cell in cells])
        
        # Create a DataFrame from the rows
        df = pd.DataFrame(rows, columns=headers)
        
        # Select only the 'Symbol' and 'Name' columns
        df = df[['Symbol', 'Name']]
        
        # Add a column for the category (Stocks, ETFs, Crypto)
        df['Category'] = category
        
        # Append the DataFrame to the list
        dfs.append(df)

    # Concatenate all DataFrames into one
    ticker_df = pd.concat(dfs, ignore_index=True)
    ticker_df = ticker_df.sort_values(by=['Category', 'Symbol'], ascending=[False, True])

    #seperates stocks and etf from crypto due to different trading schedules
    stock_etf_df =ticker_df[ticker_df['Category'].isin(['Stocks', 'ETFs'])]
    stock_etf_df['Name_Category'] = stock_etf_df.apply(lambda row: f"{row['Name']} - {row['Category']}", axis=1)
    stock_etf_dict = stock_etf_df.set_index('Symbol')['Name_Category'].to_dict()

    crypto_df = ticker_df[ticker_df['Category'] == 'Crypto']
    crypto_df['Name_Category'] = crypto_df.apply(lambda row: f"{row['Name']} - {row['Category']}", axis=1)
    crypto_dict = crypto_df.set_index('Symbol')['Name_Category'].to_dict()

    # Convert the DataFrame to a dictionary
    return stock_etf_dict, crypto_dict


st.title("Portfolio Performance Analyzer")
st.write("This interactive dashboard empowers you to compare the performance of multiple stocks and ETFs side-by-side. Analyze historical price trends, percentage changes, and calculate potential returns on your investments over a chosen timeframe. Visualize your data with ease and gain valuable insights to inform your investment decisions.")
st.write('All Data sourced from Yahoo Finance Database')

# Predefined list of popular tickers with their full company names
stock_etf_dict, crypto_dict = get_ticker_list()

# Sidebar for user input
st.sidebar.header("User Input")

# Dropdown for selecting tickers
selected_tickers = st.sidebar.multiselect(
    "Select stock tickers",
    options=[f"{ticker} - {name}" for ticker, name in stock_etf_dict.items()],
    # default=["AAPL - Apple Inc. - Stocks", "SPY - SPDR S&P 500 ETF Trust - ETFs"]
)

# Manual input for tickers
manual_tickers = st.sidebar.text_input("Or enter stock tickers manually (comma separated)", "AAPL, NVDA, HIMS")

# Combine selected tickers from dropdown and manual input
tickers = [ticker.split(" - ")[0] for ticker in selected_tickers]
if manual_tickers:
    tickers.extend([ticker.strip() for ticker in manual_tickers.split(",")])

# Date range selection
start_date = st.sidebar.date_input("Start date", pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("End date", pd.to_datetime("today"))

# Fetch data from Yahoo Finance
@st.cache_data
def get_data(tickers, start_date, end_date):
    ticker_list = [ticker.strip() for ticker in tickers]
    try:
        data = yf.download(ticker_list, start=start_date, end=end_date, group_by='ticker', auto_adjust=False)
        adj_close_data = pd.DataFrame()
        for ticker in ticker_list:
            if ticker in data:
                adj_close_data[ticker] = data[ticker]['Adj Close']
            else:
                st.warning(f"Ticker {ticker} not found or has no data.")
        return adj_close_data
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()

data = get_data(tickers, start_date, end_date)

# Display the data in page
if not data.empty:
    st.write("#### ROI")  
    st.write(f"{start_date.strftime('%Y/%m/%d')} to {end_date.strftime('%Y/%m/%d')}")   
    st.write("Discover how your investments grow over time! Enter your initial investment amount and select a time period to calculate your potential return on investment (ROI). Visualize the performance of your investments with interactive charts, tracking daily, weekly, and monthly growth or decline. This tool helps you make informed financial decisions whether you're planning for the future or analyzing past performance,")
    col3, col4 = st.columns(2, gap='Large')
    with col3:
        # Calculate ROI based on the initial investment amount
        investment_amount = st.number_input("Enter investment amount ($)", min_value=0, value=1000)

    with col4:
        roi_data = []
        growth_data = pd.DataFrame(index=data.index)
        for ticker in data.columns:
            initial_price = data[ticker].iloc[0]
            latest_price = data[ticker].iloc[-1]
            shares_purchased = investment_amount / initial_price
            final_value = round(shares_purchased * latest_price, 2)
            roi = round(final_value - investment_amount, 2)
            roi_percentage = round(((latest_price - initial_price) / initial_price) * 100, 2)  # Same as growth rate
            # Calculate growth or decline for each date
            growth_data[ticker] = (data[ticker] / initial_price - 1) * investment_amount

            roi_data.append({
                "Ticker": ticker,
                "Initial Price": round(initial_price, 2),
                "Latest Price": round(latest_price, 2),
                "Shares Purchased": round(shares_purchased, 2),
                "Final Value": final_value,
                "ROI ($)": roi,
                "ROI (%)": roi_percentage
            })

        roi_df = pd.DataFrame(roi_data)
        st.write("ROI Data Table")
        st.write(roi_df)
  
    # Add a dropdown menu for selecting the view for growth rate comparison
    view_option = st.selectbox(
        "Select view for growth rate chart",
        options=["Daily", "Monthly", "Yearly"],
        index=1  # Default to Monthly
    )

    # Plot the growth or decline of the investment amount
    st.write("#### Growth or Decline of Investment Amount")
    fig_growth = px.line(growth_data, x=growth_data.index, y=growth_data.columns, labels={'value': 'Growth/Decline ($)'}, title='Investment Growth Over Time Chart')
    st.plotly_chart(fig_growth, use_container_width=True)

    st.write("#### Price Comparison")
    
    col1, col2 = st.columns(2, gap='Large')
    with col1:
        st.write("Comparison Chart")
        fig = px.line(data, x=data.index, y=data.columns)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.write("Adj Close Prices Ordered by Date")
        st.write(data)

    # Calculate metrics
    st.write("### Key Metrics")
    metrics = []
    for ticker in data.columns:
        latest_price = data[ticker].iloc[-1]
        initial_price = data[ticker].iloc[0]
        growth_rate = ((latest_price - initial_price) / initial_price) * 100  # Growth rate in percentage
        # daily_change = ((latest_price - data[ticker].iloc[-2]) / data[ticker].iloc[-2]) * 100  # Daily change in percentage
        volatility = data[ticker].pct_change().std() * np.sqrt(252)  # Annualized volatility
        cumulative_return = ((latest_price - initial_price) / initial_price) * 100  # Cumulative return in percentage

        # Fetch additional info using yfinance Ticker
        stock_info = yf.Ticker(ticker).info
        dividend_yield = stock_info.get('dividendYield', None) 
        pe_ratio = stock_info.get('trailingPE', None) 
        market_cap = stock_info.get('marketCap', None)  
        sector = stock_info.get('sector', 'N/A') 

        metrics.append({
            "Ticker": ticker,
            "Latest Price": round(latest_price, 2),
            # "Daily Change (%)": round(daily_change, 2),
            "Growth Rate (%)": round(growth_rate, 2),
            "Volatility (%)": round(volatility * 100, 2),  # Volatility in percentage
            "Dividend Yield (%)": round(dividend_yield * 100, 2) if dividend_yield else "N/A",
            "P/E Ratio": round(pe_ratio, 2) if pe_ratio else "N/A",
            "Market Cap (B)": f"{round(market_cap / 1e9, 2)}B" if market_cap else "N/A",
            "Sector": sector if sector else "N/A",
        })
    
    # Convert metrics to a DataFrame and display as a table
    metrics_df = pd.DataFrame(metrics)
    st.table(metrics_df)

    # Fetch description of the selected ticker
    descriptions = {}
    st.write("### Description")
    for ticker in tickers:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        description = info.get('shortBusinessSummary') or info.get('longBusinessSummary', 'No description available.')  # Fetch short or long description
        descriptions[ticker] = description  # Store description in the dictionary
        st.write(f"**{ticker}**:")
        st.write(description)

    st.write("**Disclaimer**: This dashboard is for informational purposes only and should not be considered financial advice. Please conduct your own research before making any investment decisions.")

else:
    st.warning("Select one or more tickers to begin.")
