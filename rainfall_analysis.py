import requests
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st

def get_monthly_rainfall_analysis(latitude, longitude, start_year=2007, end_date="2024-07-31"):
    """
    Get and analyze monthly rainfall data from 2007 to July 2024
    """
    start_date = f"{start_year}0101"
    
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    params = {
        "parameters": "PRECTOTCORR",
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date,
        "end": end_date.replace("-", ""),
        "format": "JSON"
    }
    
    try:
        # Print request details for debugging
        st.write(f"Requesting data from: {base_url}")
        st.write(f"With parameters: {params}")
        
        response = requests.get(base_url, params=params)
        
        # Print response status and content for debugging
        st.write(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            st.write(f"Error response content: {response.text}")
            return None
            
        response.raise_for_status()
        
        data = response.json()
        
        # Verify data structure
        if 'properties' not in data or 'parameter' not in data['properties'] or 'PRECTOTCORR' not in data['properties']['parameter']:
            st.write(f"Unexpected data structure: {data}")
            return None
            
        rainfall_data = data['properties']['parameter']['PRECTOTCORR']
        
        df = pd.DataFrame.from_dict(rainfall_data, orient='index', columns=['rainfall_mm'])
        df.index = pd.to_datetime(df.index)
        
        monthly_df = df.resample('M').sum()
        monthly_df = monthly_df[monthly_df.index <= pd.Timestamp(end_date)]
        
        return monthly_df
        
    except requests.exceptions.RequestException as e:
        st.write(f"Request error: {str(e)}")
        return None
    except ValueError as e:
        st.write(f"Data processing error: {str(e)}")
        return None
    except Exception as e:
        st.write(f"Unexpected error: {str(e)}")
        return None

def plot_rainfall_analysis(monthly_df, latitude, longitude):
    """Create detailed visualizations"""
    # ... existing code ...
    fig, axes = plt.subplots(3, 1, figsize=(15, 20))
    
    # 1. Monthly Rainfall Timeline
    axes[0].plot(monthly_df.index, monthly_df['rainfall_mm'], 
                label='Monthly Rainfall', color='blue', alpha=0.6)
    axes[0].plot(monthly_df.index, 
                monthly_df['rainfall_mm'].rolling(window=12).mean(),
                label='12-Month Rolling Average', color='red', linewidth=2)
    axes[0].set_title(f'Monthly Rainfall Timeline (2007 - July 2024)\nCoordinates: {latitude}, {longitude}')
    axes[0].set_xlabel('Date')
    axes[0].set_ylabel('Rainfall (mm)')
    axes[0].legend()
    axes[0].grid(True)
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].set_xlim(monthly_df.index[0], monthly_df.index[-1])
    
    # 2. Annual Totals
    yearly = monthly_df.resample('Y')['rainfall_mm'].sum()
    axes[1].bar(yearly.index.year, yearly.values, color='green', alpha=0.6)
    axes[1].set_title('Annual Rainfall Totals')
    axes[1].set_xlabel('Year')
    axes[1].set_ylabel('Total Rainfall (mm)')
    axes[1].grid(True)
    axes[1].set_xlim(yearly.index.year[0] - 0.5, yearly.index.year[-1] + 0.5)
    
    # 3. Monthly Averages
    monthly_avg = monthly_df.groupby(monthly_df.index.month)['rainfall_mm'].mean()
    axes[2].bar(range(1, 13), monthly_avg, color='blue', alpha=0.6)
    axes[2].set_title('Average Rainfall by Month')
    axes[2].set_xlabel('Month')
    axes[2].set_ylabel('Average Rainfall (mm)')
    axes[2].set_xticks(range(1, 13))
    axes[2].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    axes[2].grid(True)
    
    plt.tight_layout()
    return fig

def get_summary_statistics(monthly_df):
    """Calculate and return summary statistics"""
    stats = {
        "avg_monthly": monthly_df['rainfall_mm'].mean(),
        "max_monthly": monthly_df['rainfall_mm'].max(),
        "min_monthly": monthly_df['rainfall_mm'].min(),
        "total_years": len(monthly_df.index.year.unique())
    }
    
    # Calculate seasonal statistics
    monthly_df['season'] = pd.cut(monthly_df.index.month, 
                                 bins=[0,3,6,9,12], 
                                 labels=['Summer', 'Autumn', 'Winter', 'Spring'])
    stats["seasonal_avg"] = monthly_df.groupby('season')['rainfall_mm'].mean()
    
    return stats 