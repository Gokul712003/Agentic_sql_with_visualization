import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from langchain.tools import Tool
from datetime import datetime
from visualization import create_price_trend_chart, create_volume_chart, create_price_volume_chart, create_moving_average_chart, create_comparative_chart, generate_visualization_summary

# Load environment variables
load_dotenv()

llm = LLM(
    model='gemini/gemini-2.0-flash',
    api_key=os.getenv("GOOGLE_API_KEY"),
)
# Database connection function
def get_db_connection():
    conn = sqlite3.connect('stocks.db')
    conn.row_factory = sqlite3.Row
    return conn

# Tool for executing SQL queries
def execute_sql_query(query, params=None):
    try:
        conn = get_db_connection()
        if params is None:
            # For read-only schema queries
            df = pd.read_sql_query(query, conn)
        else:
            # For parameterized queries
            df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        return f"Error executing query: {str(e)}"

# Tool for getting available tables and schema
def get_db_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_info = {}
    
    # Get schema for each table
    for table in tables:
        table_name = table['name']
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        schema_info[table_name] = [{'name': col['name'], 'type': col['type']} for col in columns]
    
    conn.close()
    return schema_info



# Define tools
sql_tool = Tool(
    name="SQLQueryTool",
    func=execute_sql_query,
    description="Execute SQL queries on the stock database with optional parameters for security"
)

schema_tool = Tool(
    name="DBSchemaTool",
    func=get_db_schema,
    description="Get the database schema information"
)

# Visualization tools
def create_line_chart_tool(df, symbol):
    # Convert string to DataFrame if needed
    if isinstance(df, str):
        import io
        df = pd.read_csv(io.StringIO(df), delim_whitespace=True)
    try:
        return create_price_trend_chart(df, symbol, chart_type='line')
    except Exception as e:
        error_msg = f"Error creating line chart: {str(e)}"
        print(error_msg)
        return generate_visualization_summary([], symbol, error_msg)

def create_candlestick_chart_tool(df, symbol):
    # Convert string to DataFrame if needed
    if isinstance(df, str):
        import io
        df = pd.read_csv(io.StringIO(df), delim_whitespace=True)
    try:
        return create_price_trend_chart(df, symbol, chart_type='candlestick')
    except Exception as e:
        error_msg = f"Error creating candlestick chart: {str(e)}"
        print(error_msg)
        return generate_visualization_summary([], symbol, error_msg)

line_chart_tool = Tool(
    name="LineChartTool",
    func=create_line_chart_tool,
    description="Create a line chart showing stock price trends over time"
)

candlestick_tool = Tool(
    name="CandlestickChartTool",
    func=create_candlestick_chart_tool,
    description="Create a candlestick chart showing stock price OHLC data"
)

# Wrapper functions for other visualization tools
def create_volume_chart_tool(df, symbol):
    # Convert string to DataFrame if needed
    if isinstance(df, str):
        import io
        df = pd.read_csv(io.StringIO(df), delim_whitespace=True)
    try:
        return create_volume_chart(df, symbol)
    except Exception as e:
        error_msg = f"Error creating volume chart: {str(e)}"
        print(error_msg)
        return generate_visualization_summary([], symbol, error_msg)

def create_price_volume_chart_tool(df, symbol):
    # Convert string to DataFrame if needed
    if isinstance(df, str):
        import io
        df = pd.read_csv(io.StringIO(df), delim_whitespace=True)
    try:
        return create_price_volume_chart(df, symbol)
    except Exception as e:
        error_msg = f"Error creating price-volume chart: {str(e)}"
        print(error_msg)
        return generate_visualization_summary([], symbol, error_msg)

def create_moving_average_chart_tool(df, symbol, window_sizes=[20, 50]):
    # Convert string to DataFrame if needed
    if isinstance(df, str):
        import io
        df = pd.read_csv(io.StringIO(df), delim_whitespace=True)
    try:
        return create_moving_average_chart(df, symbol, window_sizes)
    except Exception as e:
        error_msg = f"Error creating moving average chart: {str(e)}"
        print(error_msg)
        return generate_visualization_summary([], symbol, error_msg)

volume_chart_tool = Tool(
    name="VolumeChartTool",
    func=create_volume_chart_tool,
    description="Create a bar chart showing trading volume over time"
)

price_volume_tool = Tool(
    name="PriceVolumeTool",
    func=create_price_volume_chart_tool,
    description="Create a combined chart with price trend and volume"
)

moving_average_tool = Tool(
    name="MovingAverageTool",
    func=create_moving_average_chart_tool,
    description="Create a chart with moving averages"
)

# Define agents
data_analyst_agent = Agent(
    role="Data Analyst",
    goal="Analyze stock data and extract meaningful insights",
    backstory="You are an expert data analyst with years of experience in financial data analysis.",
    verbose=True,
    llm=llm,
    tools=[sql_tool, schema_tool]
)

visualization_agent = Agent(
    role="Data Visualization Specialist",
    goal="Create insightful visualizations from stock data",
    backstory="You are an expert in data visualization with a focus on financial markets. You know how to represent data visually to reveal patterns and insights.",
    verbose=True,
    llm=llm,
    tools=[line_chart_tool, candlestick_tool, volume_chart_tool, price_volume_tool, moving_average_tool]
)

def process_user_query(user_input):
    # Task for data analysis
    analysis_task = Task(
        description=f"Analyze the following user query and extract relevant stock data: '{user_input}'. "
                   f"First, understand the database schema. Then, write and execute appropriate SQL queries to get the data. "
                   f"Return the data in a detailed, readable format with insights about the query results.",
        expected_output="A pandas DataFrame containing the relevant stock data based on the user query with analysis",
        agent=data_analyst_agent,
        output_file="report.md"
    )
    
    # Task for data visualization
    visualization_task = Task(
        description=f"Create visualizations for the stock data related to: '{user_input}'. "
                   f"Use the data provided by the Data Analyst to generate appropriate charts. "
                   f"Consider what type of visualization would best represent the data and insights.",
        expected_output="A set of visualization files and a summary markdown file",
        agent=visualization_agent,
        context=[analysis_task],
        output_file="visualizations/visualization_summary.md"
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[data_analyst_agent, visualization_agent],
        tasks=[analysis_task, visualization_task],
        verbose=True
    )
    
    result = crew.kickoff()
    
    return result



def main():
    print("Welcome to the Stock Data Analysis System!")
    print("Type 'exit' to quit the application.")
    
    while True:
        user_input = input("\nEnter your query (e.g., 'Show me Apple's stock price trend for the last 6 months'): ")
        
        if user_input.lower() == 'exit':
            print("Thank you for using the Stock Data Analysis System. Goodbye!")
            break
        
        print("\nProcessing your query. This may take a moment...")
        result = process_user_query(user_input)
        print("\nResults:")
        print(result)
        print("\nAnalysis output has been saved to the 'report.md' file.")
        print("Visualizations have been saved to the 'visualizations' directory.")
        print("A summary of visualizations is available in 'visualizations/visualization_summary.md'.")

if __name__ == "__main__":
    main()