import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Create visualizations directory if it doesn't exist
def ensure_visualization_dir():
    vis_dir = 'visualizations'
    if not os.path.exists(vis_dir):
        os.makedirs(vis_dir)
    return vis_dir

# Helper function to safely process dataframes with date columns
def process_dataframe_dates(df, date_column='date'):
    """Process dataframe to ensure dates are properly formatted
    
    Args:
        df: Pandas DataFrame containing stock data
        date_column: Name of the date column (default: 'date')
        
    Returns:
        Processed DataFrame with properly formatted dates
        
    Raises:
        ValueError: If date parsing fails completely
    """
    # Make a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Check if the date column exists
    if date_column not in df_copy.columns:
        raise ValueError(f"Date column '{date_column}' not found in the dataframe")
    
    # Format the date if it's a string with robust error handling
    if df_copy[date_column].dtype == 'object':
        try:
            # Try automatic parsing first
            df_copy[date_column] = pd.to_datetime(df_copy[date_column])
        except Exception as e:
            # Try common date formats
            date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y%m%d', '%b %d %Y', '%d-%b-%Y', '%d-%m-%Y']
            
            for date_format in date_formats:
                try:
                    df_copy[date_column] = pd.to_datetime(df_copy[date_column], format=date_format)
                    print(f"Successfully parsed dates using format: {date_format}")
                    break
                except Exception:
                    continue
            else:
                # If all formats fail, try with errors='coerce' to set unparseable dates to NaT
                try:
                    df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
                    # Drop rows with NaT values
                    original_len = len(df_copy)
                    df_copy = df_copy.dropna(subset=[date_column])
                    if len(df_copy) < original_len:
                        print(f"Warning: Dropped {original_len - len(df_copy)} rows with unparseable dates")
                    if len(df_copy) == 0:
                        raise ValueError("All date values were unparseable")
                except Exception as e:
                    raise ValueError(f"Unable to parse date column: {str(e)}. Please check the date format.")
    
    # Sort by date
    df_copy = df_copy.sort_values(date_column)
    
    return df_copy

# Line chart for stock price trends
def create_price_trend_chart(df, symbol, chart_type='line'):
    """Create a line chart showing price trends over time"""
    vis_dir = ensure_visualization_dir()
    
    # Process dates using the helper function
    df = process_dataframe_dates(df)
    
    # Create the visualization based on chart type
    if chart_type == 'line':
        fig = px.line(df, x='date', y='close', title=f'{symbol} Stock Price Trend')
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Closing Price ($)',
            template='plotly_white'
        )
        output_path = f"{vis_dir}/{symbol}_price_trend.html"
        fig.write_html(output_path)
        
    elif chart_type == 'candlestick':
        fig = go.Figure(data=[go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])
        fig.update_layout(
            title=f'{symbol} Stock Price Candlestick Chart',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white'
        )
        output_path = f"{vis_dir}/{symbol}_candlestick.html"
        fig.write_html(output_path)
    
    return output_path

# Volume chart
def create_volume_chart(df, symbol):
    """Create a bar chart showing trading volume over time"""
    vis_dir = ensure_visualization_dir()
    
    # Process dates using the helper function
    df = process_dataframe_dates(df)
    
    fig = px.bar(df, x='date', y='volume', title=f'{symbol} Trading Volume')
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Volume',
        template='plotly_white'
    )
    
    output_path = f"{vis_dir}/{symbol}_volume.html"
    fig.write_html(output_path)
    return output_path

# Price and volume combined chart
def create_price_volume_chart(df, symbol):
    """Create a combined chart with price trend and volume"""
    vis_dir = ensure_visualization_dir()
    
    # Process dates using the helper function
    df = process_dataframe_dates(df)
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['close'],
        name='Closing Price',
        line=dict(color='royalblue')
    ))
    
    # Add volume bars
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['volume'],
        name='Volume',
        yaxis='y2',
        marker=dict(color='lightgray')
    ))
    
    # Set layout with secondary y-axis
    fig.update_layout(
        title=f'{symbol} Price and Volume',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        yaxis2=dict(
            title='Volume',
            titlefont=dict(color='gray'),
            tickfont=dict(color='gray'),
            overlaying='y',
            side='right'
        ),
        template='plotly_white'
    )
    
    output_path = f"{vis_dir}/{symbol}_price_volume.html"
    fig.write_html(output_path)
    return output_path

# Moving average chart
def create_moving_average_chart(df, symbol, window_sizes=[20, 50]):
    """Create a chart with moving averages"""
    vis_dir = ensure_visualization_dir()
    
    # Process dates using the helper function
    df = process_dataframe_dates(df)
    
    # Calculate moving averages
    for window in window_sizes:
        df[f'MA_{window}'] = df['close'].rolling(window=window).mean()
    
    # Create figure
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['close'],
        name='Closing Price',
        line=dict(color='black', width=1)
    ))
    
    # Add moving average lines
    colors = ['blue', 'red', 'green', 'purple']
    for i, window in enumerate(window_sizes):
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df[f'MA_{window}'],
            name=f'{window}-day MA',
            line=dict(color=colors[i % len(colors)], width=1.5)
        ))
    
    # Set layout
    fig.update_layout(
        title=f'{symbol} Price with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='plotly_white'
    )
    
    output_path = f"{vis_dir}/{symbol}_moving_averages.html"
    fig.write_html(output_path)
    return output_path

# Comparative analysis chart for multiple stocks
def create_comparative_chart(data_dict):
    """Create a chart comparing multiple stocks
    
    Args:
        data_dict: Dictionary with stock symbols as keys and dataframes as values
    """
    vis_dir = ensure_visualization_dir()
    
    fig = go.Figure()
    
    # Add each stock's price line
    for symbol, df in data_dict.items():
        # Process dates using the helper function
        df = process_dataframe_dates(df)
        
        # Normalize to percentage change from first day for fair comparison
        first_price = df['close'].iloc[0]
        df['normalized'] = (df['close'] / first_price - 1) * 100
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['normalized'],
            name=symbol
        ))
    
    # Set layout
    fig.update_layout(
        title='Comparative Stock Performance',
        xaxis_title='Date',
        yaxis_title='Percentage Change (%)',
        template='plotly_white'
    )
    
    output_path = f"{vis_dir}/comparative_analysis.html"
    fig.write_html(output_path)
    return output_path

# Generate summary of all visualizations
def generate_visualization_summary(created_visualizations, symbol=None, error_message=None):
    """Generate a markdown summary of all created visualizations
    
    Args:
        created_visualizations: List of paths to created visualization files
        symbol: Stock symbol for the title
        error_message: Optional error message to display if visualizations failed
    """
    vis_dir = ensure_visualization_dir()
    
    # Create title based on symbol if provided
    if symbol:
        summary = f"# {symbol} Stock Analysis\n\n"
    else:
        summary = "# Stock Data Visualizations\n\n"
    
    # Handle error case
    if error_message:
        summary += f"**Note:** {error_message}\n\n"
    
    # If we have visualizations, list them
    if created_visualizations and len(created_visualizations) > 0:
        summary += "The following visualizations have been generated:\n\n"
        
        for i, vis_path in enumerate(created_visualizations, 1):
            file_name = os.path.basename(vis_path)
            summary += f"{i}. [{file_name}]({vis_path})\n"
        
        summary += "\n\nTo view these visualizations, open the HTML files in your web browser."
    else:
        # If no visualizations were created but also no error, provide a generic message
        if not error_message:
            summary += "No visualizations were generated. Please check the data format and try again."
    
    with open(f"{vis_dir}/visualization_summary.md", 'w') as f:
        f.write(summary)
    
    return f"{vis_dir}/visualization_summary.md"