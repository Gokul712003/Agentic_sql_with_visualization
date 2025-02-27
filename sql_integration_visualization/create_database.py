import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create a connection to the SQLite database
conn = sqlite3.connect('stocks.db')
cursor = conn.cursor()

# Create tables for stock data
cursor.execute('''
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    company_name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS stock_prices (
    id INTEGER PRIMARY KEY,
    stock_id INTEGER,
    date TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stocks (id)
)
''')

# Sample stock data
stocks = [
    (1, 'AAPL', 'Apple Inc.'),
    (2, 'MSFT', 'Microsoft Corporation'),
    (3, 'GOOGL', 'Alphabet Inc.'),
    (4, 'AMZN', 'Amazon.com, Inc.'),
    (5, 'META', 'Meta Platforms, Inc.')
]

# Insert stock data
cursor.executemany('INSERT OR REPLACE INTO stocks VALUES (?, ?, ?)', stocks)

# Generate random stock price data for the past 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days

stock_prices = []
price_id = 1

for stock_id in range(1, 6):
    # Initial price between $100 and $500
    base_price = np.random.uniform(100, 500)
    
    for date in dates:
        # Random daily volatility
        daily_volatility = np.random.uniform(0.005, 0.02)
        
        # Generate OHLC data
        open_price = base_price * (1 + np.random.uniform(-daily_volatility, daily_volatility))
        high_price = open_price * (1 + np.random.uniform(0, daily_volatility * 2))
        low_price = open_price * (1 - np.random.uniform(0, daily_volatility * 2))
        close_price = np.random.uniform(low_price, high_price)
        
        # Random volume between 1M and 10M
        volume = int(np.random.uniform(1000000, 10000000))
        
        # Add some trends and patterns
        if np.random.random() < 0.6:  # 60% chance to follow previous trend
            base_price = close_price
        else:
            # Random shift
            base_price = base_price * (1 + np.random.uniform(-0.03, 0.03))
        
        stock_prices.append((
            price_id,
            stock_id,
            date.strftime('%Y-%m-%d'),
            round(open_price, 2),
            round(high_price, 2),
            round(low_price, 2),
            round(close_price, 2),
            volume
        ))
        price_id += 1

# Insert stock price data
cursor.executemany('''
INSERT OR REPLACE INTO stock_prices 
(id, stock_id, date, open, high, low, close, volume) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', stock_prices)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database created successfully with sample stock data!")