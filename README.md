# Agentic_sql_with_visualization

# SQL Integration & Stock Data Visualization

A powerful tool for analyzing and visualizing stock market data using natural language queries. This application combines SQL database integration with advanced data visualization capabilities, powered by AI agents that work together to analyze and present financial data.

## Features

- **Natural Language Processing**: Query stock data using plain English
- **SQL Database Integration**: Seamless connection to SQLite database containing stock information
- **Interactive Visualizations**: Generate dynamic, interactive charts using Plotly
- **AI-Powered Analysis**: Utilizes CrewAI and Gemini AI for intelligent data processing
- **Multiple Visualization Types**:
  - Price trend line charts
  - Candlestick charts
  - Volume charts
  - Price-volume combined charts
  - Moving average charts
  - Comparative stock analysis

## Project Structure

```
├── app.py                 # Main application file
├── create_database.py     # Script to create and populate the SQLite database
├── visualization.py       # Visualization functions and utilities
├── stocks.db             # SQLite database containing stock data
├── .env                  # Environment variables (API keys)
├── visualizations/       # Directory for generated visualization files
└── report.md             # Generated analysis reports
```

## Installation

1. Clone this repository
2. Install required dependencies:

```bash
pip install pandas matplotlib seaborn plotly crewai langchain python-dotenv
```

3. Set up your environment variables in `.env` file:
```
GOOGLE_API_KEY="your_google_api_key"
```

4. Initialize the database (if not already created):
```bash
python create_database.py
```

## Usage

1. Run the main application:
```bash
python app.py
```

2. Enter your query in natural language, for example:
   - "Show me Apple's stock price trend for the last 6 months"
   - "Compare Microsoft and Google stock performance"
   - "Analyze Amazon's trading volume patterns"

3. The application will:
   - Analyze your query using AI
   - Extract relevant data from the database
   - Generate appropriate visualizations
   - Provide a written analysis

4. Results will be saved to:
   - `report.md` - Text analysis
   - `visualizations/` directory - Interactive HTML charts
   - `visualizations/visualization_summary.md` - Summary of all generated visualizations

## How It Works

The application uses a two-agent system powered by CrewAI:

1. **Data Analyst Agent**: Interprets user queries, examines the database schema, and executes appropriate SQL queries to retrieve relevant data.

2. **Visualization Agent**: Takes the data provided by the analyst and creates appropriate visualizations based on the nature of the data and the user's query.

The system supports various visualization types including line charts, candlestick charts, volume charts, and moving averages to provide comprehensive insights into stock performance.

## Database Schema

The SQLite database (`stocks.db`) contains two main tables:

- **stocks**: Basic information about stocks
  - id (INTEGER PRIMARY KEY)
  - symbol (TEXT) - Stock ticker symbol
  - company_name (TEXT) - Full company name

- **stock_prices**: Historical price data
  - id (INTEGER PRIMARY KEY)
  - stock_id (INTEGER) - Foreign key to stocks table
  - date (TEXT) - Trading date
  - open (REAL) - Opening price
  - high (REAL) - Highest price of the day
  - low (REAL) - Lowest price of the day
  - close (REAL) - Closing price
  - volume (INTEGER) - Trading volume

## Visualization Types

### Price Trend Charts
Displays closing prices over time as a line chart, providing a clear view of price trends.

### Candlestick Charts
Shows open, high, low, and close prices in a traditional candlestick format, ideal for technical analysis.

### Volume Charts
Visualizes trading volume over time, helping identify periods of high market activity.

### Price-Volume Charts
Combines price and volume data in a single chart with dual y-axes.

### Moving Average Charts
Displays price with moving averages (typically 20-day and 50-day), useful for trend identification.

### Comparative Analysis
Compares performance of multiple stocks normalized to percentage change from a starting point.

## Requirements

- Python 3.8+
- pandas
- matplotlib
- seaborn
- plotly
- crewai
- langchain
- python-dotenv
- sqlite3

## License

This project is available for open use and modification.

## Acknowledgements

- Uses Gemini AI from Google for natural language processing
- Built with CrewAI framework for agent collaboration
- Visualizations powered by Plotly
