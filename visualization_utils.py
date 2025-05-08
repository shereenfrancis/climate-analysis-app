import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from calendar import month_abbr

def plot_monthly_distribution(rainfall_data):
    """Create a box plot showing rainfall distribution by month"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare data for box plot
    monthly_data = []
    labels = []
    for month in range(1, 13):
        month_data = rainfall_data[rainfall_data.index.month == month]['rainfall_mm']
        monthly_data.append(month_data)
        labels.append(month_abbr[month])
    
    # Create box plot
    ax.boxplot(monthly_data, labels=labels)
    ax.set_title('Monthly Rainfall Distribution')
    ax.set_xlabel('Month')
    ax.set_ylabel('Rainfall (mm)')
    ax.grid(True, alpha=0.3)
    
    return fig

def plot_rainfall_heatmap(rainfall_data):
    """Create a heatmap of rainfall patterns"""
    # Reshape data into year x month format
    pivot_data = rainfall_data.pivot_table(
        index=rainfall_data.index.year,
        columns=rainfall_data.index.month,
        values='rainfall_mm',
        aggfunc='sum'
    )
    pivot_data.columns = [month_abbr[m] for m in pivot_data.columns]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(pivot_data, cmap='YlOrRd', annot=True, fmt='.0f', ax=ax)
    ax.set_title('Rainfall Patterns Over Years')
    ax.set_xlabel('Month')
    ax.set_ylabel('Year')
    
    return fig

def plot_cumulative_rainfall(rainfall_data):
    """Plot cumulative rainfall for each year"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    years = rainfall_data.index.year.unique()
    current_year = pd.Timestamp.now().year
    
    for year in years:
        year_data = rainfall_data[rainfall_data.index.year == year]['rainfall_mm']
        cumsum = year_data.cumsum()
        
        if year == current_year:
            ax.plot(range(1, len(cumsum) + 1), cumsum, 
                   label=str(year), linewidth=3, color='red')
        else:
            ax.plot(range(1, len(cumsum) + 1), cumsum, 
                   label=str(year), alpha=0.3)
    
    ax.set_title('Cumulative Rainfall by Year')
    ax.set_xlabel('Month')
    ax.set_ylabel('Cumulative Rainfall (mm)')
    ax.grid(True)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    return fig

def plot_drought_analysis(rainfall_data):
    """Create drought analysis visualization"""
    monthly_mean = rainfall_data['rainfall_mm'].mean()
    drought_threshold = monthly_mean * 0.6
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot rainfall
    ax.plot(rainfall_data.index, rainfall_data['rainfall_mm'], 
            label='Monthly Rainfall', alpha=0.6)
    
    # Plot threshold
    ax.axhline(y=drought_threshold, color='r', linestyle='--', 
               label='Drought Threshold')
    
    # Highlight drought periods
    drought_periods = rainfall_data[rainfall_data['rainfall_mm'] < drought_threshold]
    ax.fill_between(rainfall_data.index, 0, rainfall_data['rainfall_mm'], 
                   where=rainfall_data['rainfall_mm'] < drought_threshold,
                   color='red', alpha=0.3, label='Drought Periods')
    
    ax.set_title('Drought Analysis')
    ax.set_xlabel('Date')
    ax.set_ylabel('Rainfall (mm)')
    ax.legend()
    ax.grid(True)
    
    return fig

def plot_seasonal_patterns(rainfall_data):
    """Create seasonal pattern analysis"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    
    # Average monthly rainfall
    monthly_avg = rainfall_data.groupby(rainfall_data.index.month)['rainfall_mm'].mean()
    monthly_std = rainfall_data.groupby(rainfall_data.index.month)['rainfall_mm'].std()
    
    months = [month_abbr[m] for m in range(1, 13)]
    
    # Plot average monthly rainfall with error bars
    ax1.bar(months, monthly_avg, yerr=monthly_std, capsize=5)
    ax1.set_title('Average Monthly Rainfall with Variability')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Average Rainfall (mm)')
    ax1.grid(True, alpha=0.3)
    
    # Seasonal trend
    years = rainfall_data.index.year.unique()
    seasonal_data = []
    for year in years:
        year_data = rainfall_data[rainfall_data.index.year == year]['rainfall_mm']
        if len(year_data) >= 12:  # Only include complete years
            seasonal_data.append(year_data[:12].values)
    
    seasonal_avg = np.mean(seasonal_data, axis=0)
    seasonal_std = np.std(seasonal_data, axis=0)
    
    ax2.plot(months, seasonal_avg, marker='o')
    ax2.fill_between(months, 
                    seasonal_avg - seasonal_std,
                    seasonal_avg + seasonal_std,
                    alpha=0.2)
    ax2.set_title('Seasonal Pattern with Variability')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Rainfall (mm)')
    ax2.grid(True)
    
    plt.tight_layout()
    return fig 