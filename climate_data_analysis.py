import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def get_nasa_power_data(latitude, longitude, start_year=2007, end_date="2024-07-31"):
    """Get comprehensive climate data from NASA POWER"""
    parameter_groups = {
        'Temperature': [
            "T2M",      # Temperature at 2 meters (°C)
            "T2M_MAX",  # Maximum temperature at 2 meters (°C)
            "T2M_MIN",  # Minimum temperature at 2 meters (°C)
            "T2MDEW"    # Dew point temperature at 2 meters (°C)
        ],
        'Moisture': [
            "PRECTOTCORR",  # Precipitation (mm/day)
            "RH2M",         # Relative humidity at 2 meters (%)
            "QV2M"          # Specific humidity at 2 meters (kg/kg)
        ],
        'Wind': [
            "WS2M",   # Wind speed at 2 meters (m/s)
            "WS10M",  # Wind speed at 10 meters (m/s)
            "WS50M"   # Wind speed at 50 meters (m/s)
        ],
        'Solar': [
            "ALLSKY_SFC_SW_DWN",    # All sky surface shortwave downward irradiance (W/m^2)
            "CLRSKY_SFC_SW_DWN"     # Clear sky surface shortwave downward irradiance (W/m^2)
        ],
        'Soil': [
            "SOIL_M10",  # Soil moisture at 10 cm depth (m^3/m^3)
            "SOIL_T10"   # Soil temperature at 10 cm depth (°C)
        ],
        'Atmosphere': [
            "CLOUD_AMT",  # Cloud amount (%)
            "PS"          # Surface pressure (kPa)
        ]
    }
    
    # Set up dates
    start_date = f"{start_year}0101"
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    all_data = {}
    
    # Fetch data for each group separately
    for group_name, parameters in parameter_groups.items():
        print(f"\nFetching {group_name} parameters...")
        
        params = {
            "parameters": ",".join(parameters),
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start_date,
            "end": end_date.replace("-", ""),
            "format": "JSON"
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract parameters
            for param in parameters:
                try:
                    all_data[param] = data['properties']['parameter'][param]
                    print(f"Successfully retrieved {param}")
                except KeyError:
                    print(f"Parameter {param} not available")
                    continue
                
        except Exception as e:
            print(f"Error fetching {group_name} data: {e}")
            continue
    
    if not all_data:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    df.index = pd.to_datetime(df.index)
    
    # Create monthly data
    sum_params = ['PRECTOTCORR']
    monthly_means = df.drop(sum_params, axis=1, errors='ignore').resample('M').mean()
    if 'PRECTOTCORR' in df.columns:
        monthly_sums = df[sum_params].resample('M').sum()
        monthly_df = pd.concat([monthly_means, monthly_sums], axis=1)
    else:
        monthly_df = monthly_means
    
    return df, monthly_df  # Return both daily and monthly data

def plot_climate_data(df, latitude, longitude):
    """Create grouped plots for different types of parameters"""
    # Define parameter groups for plotting
    plot_groups = {
        'Temperature': ['T2M', 'T2M_MAX', 'T2M_MIN', 'T2MDEW'],
        'Moisture': ['PRECTOTCORR', 'RH2M', 'QV2M'],
        'Wind': ['WS2M', 'WS10M', 'WS50M'],
        'Solar and Soil': ['ALLSKY_SFC_SW_DWN', 'SOIL_M10', 'SOIL_T10'],
        'Atmosphere': ['CLOUD_AMT', 'PS']
    }
    
    # Create subplots based on available groups
    available_groups = [group for group, params in plot_groups.items() 
                       if any(param in df.columns for param in params)]
    n_groups = len(available_groups)
    
    fig, axes = plt.subplots(n_groups, 1, figsize=(15, 5*n_groups))
    if n_groups == 1:
        axes = [axes]
    
    for ax, group_name in zip(axes, available_groups):
        params = plot_groups[group_name]
        available_params = [p for p in params if p in df.columns]
        
        if available_params:
            for param in available_params:
                ax.plot(df.index, df[param], label=param)
            
            ax.set_title(f'{group_name} Parameters')
            ax.grid(True)
            ax.legend()
            ax.set_xlabel('Date')
    
    plt.suptitle(f'Climate Parameters for Coordinates ({latitude}, {longitude})')
    plt.tight_layout()
    return fig

def get_parameter_description(param_code):
    """Return description for parameter codes"""
    descriptions = {
        'T2M': 'Temperature at 2m (°C)',
        'T2M_MAX': 'Maximum Temperature at 2m (°C)',
        'T2M_MIN': 'Minimum Temperature at 2m (°C)',
        'T2MDEW': 'Dew Point Temperature at 2m (°C)',
        'PRECTOTCORR': 'Precipitation (mm/day)',
        'RH2M': 'Relative Humidity at 2m (%)',
        'QV2M': 'Specific Humidity at 2m (kg/kg)',
        'WS2M': 'Wind Speed at 2m (m/s)',
        'WS10M': 'Wind Speed at 10m (m/s)',
        'WS50M': 'Wind Speed at 50m (m/s)',
        'ALLSKY_SFC_SW_DWN': 'All Sky Surface Shortwave Downward Irradiance (W/m^2)',
        'CLRSKY_SFC_SW_DWN': 'Clear Sky Surface Shortwave Downward Irradiance (W/m^2)',
        'SOIL_M10': 'Soil Moisture at 10cm Depth (m^3/m^3)',
        'SOIL_T10': 'Soil Temperature at 10cm Depth (°C)',
        'CLOUD_AMT': 'Cloud Amount (%)',
        'PS': 'Surface Pressure (kPa)'
    }
    return descriptions.get(param_code, param_code)

def analyze_temperature(df):
    """Perform detailed temperature analysis including day/night patterns"""
    # Check if data is daily or monthly
    is_daily = df.index.freq != 'M'
    if not is_daily:
        st.error("Temperature analysis requires daily data. Please use daily data instead of monthly.")
        return None
        
    temp_data = {}
    
    # Existing basic statistics
    temp_data['stats'] = {
        'mean_temp': df['T2M'].mean(),
        'max_temp_ever': df['T2M_MAX'].max(),
        'min_temp_ever': df['T2M_MIN'].min(),
        'temp_range': df['T2M_MAX'].max() - df['T2M_MIN'].min(),
        'diurnal_range': (df['T2M_MAX'] - df['T2M_MIN']).mean(),
        'days_above_30': (df['T2M_MAX'] > 30).sum(),
        'days_below_0': (df['T2M_MIN'] < 0).sum(),
        'frost_risk_days': (df['T2MDEW'] < 0).sum(),
        # Add day/night estimates
        'avg_day_temp': df['T2M_MAX'].mean(),  # Average daytime high
        'avg_night_temp': df['T2M_MIN'].mean(), # Average nighttime low
        'extreme_hot_days': (df['T2M_MAX'] > 35).sum(),  # Very hot days
        'extreme_cold_nights': (df['T2M_MIN'] < 5).sum()  # Very cold nights
    }
    
    # Add day/night analysis plot
    fig_daynight, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Day vs Night temperatures by month
    monthly_day = df.groupby(df.index.month)['T2M_MAX'].mean()
    monthly_night = df.groupby(df.index.month)['T2M_MIN'].mean()
    months = range(1, 13)
    
    ax1.plot(months, monthly_day, 'ro-', label='Average Day Temperature', linewidth=2)
    ax1.plot(months, monthly_night, 'bo-', label='Average Night Temperature', linewidth=2)
    ax1.fill_between(months, monthly_day, monthly_night, alpha=0.2)
    ax1.set_xticks(months)
    ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax1.set_title('Day vs Night Temperature Patterns')
    ax1.set_ylabel('Temperature (°C)')
    ax1.grid(True)
    ax1.legend()

    # Plot 2: Diurnal temperature range by month
    monthly_range = df.groupby(df.index.month).apply(
        lambda x: x['T2M_MAX'] - x['T2M_MIN']
    ).mean()
    
    ax2.bar(months, monthly_range, color='purple', alpha=0.6)
    ax2.set_xticks(months)
    ax2.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax2.set_title('Average Daily Temperature Range by Month')
    ax2.set_ylabel('Temperature Range (°C)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    temp_data['daynight_fig'] = fig_daynight
    
    # Add monthly day/night statistics
    temp_data['daynight_stats'] = pd.DataFrame({
        'avg_day_temp': df.groupby(df.index.month)['T2M_MAX'].mean(),
        'avg_night_temp': df.groupby(df.index.month)['T2M_MIN'].mean(),
        'day_temp_std': df.groupby(df.index.month)['T2M_MAX'].std(),
        'night_temp_std': df.groupby(df.index.month)['T2M_MIN'].std(),
        'temp_range': df.groupby(df.index.month).apply(
            lambda x: (x['T2M_MAX'] - x['T2M_MIN']).mean()
        )
    })

    # Monthly patterns
    monthly_stats = df.groupby(df.index.month).agg({
        'T2M': ['mean', 'std'],
        'T2M_MAX': 'max',
        'T2M_MIN': 'min',
        'T2MDEW': 'mean'
    })
    temp_data['monthly'] = monthly_stats
    
    # Create temperature trend plot
    fig_trend, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df['T2M'], label='Average Temperature', alpha=0.7)
    ax.plot(df.index, df['T2M_MAX'], label='Maximum Temperature', alpha=0.5)
    ax.plot(df.index, df['T2M_MIN'], label='Minimum Temperature', alpha=0.5)
    ax.fill_between(df.index, df['T2M_MIN'], df['T2M_MAX'], alpha=0.2)
    ax.set_title('Temperature Trends')
    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature (°C)')
    ax.grid(True)
    ax.legend()
    temp_data['trend_fig'] = fig_trend
    
    # Create monthly distribution plot
    fig_monthly, ax = plt.subplots(figsize=(12, 6))
    monthly_means = df.groupby(df.index.month)['T2M'].mean()
    monthly_std = df.groupby(df.index.month)['T2M'].std()
    months = range(1, 13)
    ax.bar(months, monthly_means, yerr=monthly_std, capsize=5)
    ax.set_xticks(months)
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.set_title('Monthly Temperature Distribution')
    ax.set_ylabel('Temperature (°C)')
    ax.grid(True, alpha=0.3)
    temp_data['monthly_fig'] = fig_monthly
    
    # Create temperature heatmap
    pivot_temp = df.pivot_table(
        index=df.index.year,
        columns=df.index.month,
        values='T2M',
        aggfunc='mean'
    )
    pivot_temp.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    fig_heat, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(pivot_temp, cmap='RdYlBu_r', center=0, annot=True, 
                fmt='.1f', ax=ax)
    ax.set_title('Temperature Patterns Over Years')
    ax.set_xlabel('Month')
    ax.set_ylabel('Year')
    temp_data['heat_fig'] = fig_heat
    
    # Add yearly comparison of monthly day temperatures
    fig_yearly_comp, ax = plt.subplots(figsize=(15, 8))
    
    years = df.index.year.unique()
    months = range(1, 13)
    
    # Create monthly averages for each year
    yearly_monthly_temps = {}
    for year in years:
        year_mask = df.index.year == year
        year_data = df[year_mask].resample('M')['T2M_MAX'].mean()
        yearly_monthly_temps[year] = [year_data[year_data.index.month == m].iloc[0] if len(year_data[year_data.index.month == m]) > 0 else np.nan for m in months]
    
    # Plot each year's data
    for year, temps in yearly_monthly_temps.items():
        ax.plot(months, temps, marker='o', label=str(year), alpha=0.7)
    
    ax.set_xticks(months)
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.set_title('Day Temperature Comparison Across Years')
    ax.set_ylabel('Average Day Temperature (°C)')
    ax.set_xlabel('Month')
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Year')
    plt.tight_layout()
    temp_data['yearly_comparison_fig'] = fig_yearly_comp

    # Add seasonal comparison across years
    # Define seasons
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Summer'
        elif month in [3, 4, 5]:
            return 'Autumn'
        elif month in [6, 7, 8]:
            return 'Winter'
        else:  # [9, 10, 11]
            return 'Spring'
    
    # Create seasonal data
    df['season'] = df.index.month.map(get_season)
    
    # Calculate seasonal averages for each year
    seasonal_data = pd.DataFrame()
    for year in df.index.year.unique():
        year_data = df[df.index.year == year]
        season_means = year_data.groupby('season')['T2M_MAX'].mean()
        seasonal_data[year] = season_means
    
    # Sort seasons in chronological order
    season_order = ['Spring', 'Summer', 'Autumn', 'Winter']
    seasonal_data = seasonal_data.reindex(season_order)
    
    # Create seasonal comparison plot
    fig_seasonal, ax = plt.subplots(figsize=(12, 8))
    
    # Plot seasonal data
    seasonal_data.plot(kind='bar', ax=ax, width=0.8)
    ax.set_title('Seasonal Day Temperatures by Year')
    ax.set_xlabel('Season')
    ax.set_ylabel('Average Day Temperature (°C)')
    ax.grid(True, alpha=0.3)
    ax.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    temp_data['seasonal_comparison_fig'] = fig_seasonal

    # Add seasonal statistics
    temp_data['seasonal_stats'] = pd.DataFrame({
        'avg_day_temp': seasonal_data.mean(axis=1),
        'max_day_temp': seasonal_data.max(axis=1),
        'min_day_temp': seasonal_data.min(axis=1),
        'std_day_temp': seasonal_data.std(axis=1)
    }).round(2)

    return temp_data 