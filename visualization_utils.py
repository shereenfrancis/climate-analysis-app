import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from calendar import month_abbr
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def plot_location_comparison(df1, df2, lat1, lon1, lat2, lon2):
    """Create comparative visualization of two locations"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Time series comparison
    ax1.plot(df1.index, df1['rainfall_mm'], label=f'Location 1 ({lat1:.2f}, {lon1:.2f})', color='#2E86C1')
    ax1.plot(df2.index, df2['rainfall_mm'], label=f'Location 2 ({lat2:.2f}, {lon2:.2f})', color='#E74C3C')
    ax1.set_title('Rainfall Pattern Comparison')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Rainfall (mm)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Monthly distribution comparison
    monthly1 = df1.groupby(df1.index.month)['rainfall_mm'].mean()
    monthly2 = df2.groupby(df2.index.month)['rainfall_mm'].mean()
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    x = np.arange(len(months))
    width = 0.35
    
    ax2.bar(x - width/2, monthly1, width, label=f'Location 1', color='#2E86C1', alpha=0.7)
    ax2.bar(x + width/2, monthly2, width, label=f'Location 2', color='#E74C3C', alpha=0.7)
    
    ax2.set_title('Average Monthly Rainfall Comparison')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Average Rainfall (mm)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(months)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_seasonal_comparison(df1, df2, lat1, lon1, lat2, lon2):
    """Create seasonal comparison visualization"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Calculate seasonal averages
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Summer'
        elif month in [3, 4, 5]:
            return 'Autumn'
        elif month in [6, 7, 8]:
            return 'Winter'
        else:
            return 'Spring'
    
    df1['season'] = df1.index.map(lambda x: get_season(x.month))
    df2['season'] = df2.index.map(lambda x: get_season(x.month))
    
    seasonal1 = df1.groupby('season')['rainfall_mm'].mean()
    seasonal2 = df2.groupby('season')['rainfall_mm'].mean()
    
    # Reorder seasons
    seasons = ['Summer', 'Autumn', 'Winter', 'Spring']
    seasonal1 = seasonal1.reindex(seasons)
    seasonal2 = seasonal2.reindex(seasons)
    
    x = np.arange(len(seasons))
    width = 0.35
    
    ax.bar(x - width/2, seasonal1, width, label=f'Location 1', color='#2E86C1', alpha=0.7)
    ax.bar(x + width/2, seasonal2, width, label=f'Location 2', color='#E74C3C', alpha=0.7)
    
    ax.set_title('Seasonal Rainfall Comparison')
    ax.set_xlabel('Season')
    ax.set_ylabel('Average Rainfall (mm)')
    ax.set_xticks(x)
    ax.set_xticklabels(seasons)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_interactive_soil_moisture(soil_df, lat, lon):
    """Create interactive soil moisture plot with selectable layers
    
    Data source: NASA POWER (power.larc.nasa.gov)
    Parameters measured:
    - Profile Soil Moisture: Average moisture content through the soil profile (0-200cm)
    - Root Zone Soil Moisture: Moisture in root zone layer (0-100cm)
    - Surface Soil Moisture: Top layer moisture content (0-5cm)
    
    All values are in m³/m³ (volumetric water content)
    Temporal resolution: Daily
    Spatial resolution: 0.5° x 0.5°
    """
    
    # Create figure with single y-axis and template
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    # Set the template to dark
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='black',
        paper_bgcolor='black'
    )
    
    moisture_types = {
        'Profile_Soil_Wetness_%': 'Profile Soil Moisture',
        'Root_Zone_Soil_Wetness_%': 'Root Zone Soil Moisture',
        'Surface_Soil_Wetness_%': 'Surface Soil Moisture'
    }
    
    # Brighter colors for dark theme
    colors = {
        'Profile_Soil_Wetness_%': '#00B4D8',    # Bright Blue
        'Root_Zone_Soil_Wetness_%': '#90E0EF',  # Light Blue
        'Surface_Soil_Wetness_%': '#48CAE4'     # Medium Blue
    }
    
    # Convert index to datetime if needed
    if not isinstance(soil_df.index, pd.DatetimeIndex):
        soil_df.index = pd.to_datetime(soil_df.index)
    
    # Calculate moving averages for smoother lines
    for col in moisture_types.keys():
        if col in soil_df.columns:
            soil_df[f'{col}_MA'] = soil_df[col].rolling(window=7).mean()
    
    # Add traces for each moisture type
    for col, name in moisture_types.items():
        if col in soil_df.columns:
            # Add the main line
            fig.add_trace(
                go.Scatter(
                    x=soil_df.index,
                    y=soil_df[col],
                    name=name,
                    line=dict(
                        color=colors[col],
                        width=1.5,
                    ),
                    mode='lines',
                    hovertemplate=name + ': %{y:.3f}<br>Date: %{x}<extra></extra>',
                    visible=True if col == 'Root_Zone_Soil_Wetness_%' else 'legendonly',
                    showlegend=True
                )
            )
            
            # Add the moving average line
            fig.add_trace(
                go.Scatter(
                    x=soil_df.index,
                    y=soil_df[f'{col}_MA'],
                    name=f"{name} (7-day MA)",
                    line=dict(
                        color=colors[col],
                        width=3,
                        dash='dot'
                    ),
                    mode='lines',
                    hovertemplate=name + ' (7-day MA): %{y:.3f}<br>Date: %{x}<extra></extra>',
                    visible=True if col == 'Root_Zone_Soil_Wetness_%' else 'legendonly',
                    showlegend=True
                )
            )
    
    # Update layout with dark theme
    fig.update_layout(
        title=dict(
            text=f'Soil Moisture Analysis for ({lat:.2f}, {lon:.2f})',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='white')
        ),
        height=700,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0, 0, 0, 0.5)",
            bordercolor="rgba(255, 255, 255, 0.3)",
            borderwidth=1,
            font=dict(size=12, color='white')
        ),
        margin=dict(l=60, r=60, t=80, b=50),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.0,
                y=1.1,
                showactive=True,
                buttons=[
                    dict(
                        label="All Layers",
                        method="update",
                        args=[{"visible": [True] * (len(moisture_types) * 2)}]
                    ),
                    dict(
                        label="Profile",
                        method="update",
                        args=[{"visible": [True, True, False, False, False, False]}]
                    ),
                    dict(
                        label="Root Zone",
                        method="update",
                        args=[{"visible": [False, False, True, True, False, False]}]
                    ),
                    dict(
                        label="Surface",
                        method="update",
                        args=[{"visible": [False, False, False, False, True, True]}]
                    )
                ],
                font=dict(size=12, color='white'),
                bgcolor='rgba(0, 0, 0, 0.5)',
                bordercolor='rgba(255, 255, 255, 0.3)',
                borderwidth=1
            )
        ]
    )
    
    # Enhanced axes with dark theme
    fig.update_xaxes(
        title_text="Date",
        title_font=dict(color='white'),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255, 255, 255, 0.1)',
        zeroline=False,
        tickfont=dict(color='white'),
        rangeslider=dict(
            visible=True,
            thickness=0.05,
            bgcolor='rgba(0, 0, 0, 0.5)'
        ),
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            font=dict(size=10, color='white'),
            bgcolor='rgba(0, 0, 0, 0.5)',
            activecolor='rgba(255, 255, 255, 0.2)'
        )
    )
    
    fig.update_yaxes(
        title_text="Soil Moisture",
        title_font=dict(color='white'),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255, 255, 255, 0.1)',
        zeroline=False,
        range=[0, 1],
        tickformat='.2f',
        tickfont=dict(color='white')
    )
    
    return fig