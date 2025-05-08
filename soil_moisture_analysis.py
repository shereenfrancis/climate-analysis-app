import requests
import pandas as pd
import matplotlib.pyplot as plt

def get_soil_moisture_data(latitude, longitude, start_year=2007, end_date="2024-07-31"):
    """
    Get soil moisture data from NASA POWER API
    """
    start_date = f"{start_year}0101"
    
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    params = {
        "parameters": "GWETPROF,GWETROOT,GWETTOP",  # Soil moisture parameters
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
        
        # Extract soil moisture data
        soil_data = data['properties']['parameter']
        
        # Create DataFrame
        df = pd.DataFrame({
            'Profile_Soil_Wetness_%': soil_data['GWETPROF'],
            'Root_Zone_Soil_Wetness_%': soil_data['GWETROOT'],
            'Surface_Soil_Wetness_%': soil_data['GWETTOP']
        })
        
        df.index = pd.to_datetime(df.index)
        
        return df
        
    except Exception as e:
        print(f"Error fetching soil moisture data: {e}")
        return None

def plot_soil_moisture(df, latitude, longitude):
    """
    Create soil moisture visualization
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(df.index, df['Root_Zone_Soil_Wetness_%'], 
            label='Root Zone Soil Wetness', linewidth=1.5)
    ax.plot(df.index, df['Surface_Soil_Wetness_%'], 
            label='Surface Soil Wetness', linewidth=1.5)
    ax.plot(df.index, df['Profile_Soil_Wetness_%'], 
            label='Profile Soil Wetness', linewidth=1.5)

    ax.set_xlabel('Date')
    ax.set_ylabel('Soil Wetness Percentage (%)')
    ax.set_title(f'Soil Moisture Levels Over Time\nCoordinates: {latitude}, {longitude}')
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    return fig

def get_soil_moisture_stats(df):
    """
    Calculate summary statistics for soil moisture data
    """
    stats = {}
    for column in df.columns:
        name = column.replace('_', ' ')
        stats[name] = {
            'mean': df[column].mean(),
            'max': df[column].max(),
            'min': df[column].min()
        }
    return stats 