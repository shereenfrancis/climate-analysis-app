import folium
import numpy as np
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import matplotlib.dates as mdates

def create_single_grid_cell(latitude, longitude, start_date=None, end_date=None):
    """Create a single grid cell visualization with optional temporal data"""
    if start_date and end_date:
        return create_temporal_grid_cell(latitude, longitude, start_date, end_date)
    else:
        # Create map with satellite layers
        m = folium.Map(
            location=[latitude, longitude],
            zoom_start=12,
            tiles='Stamen Terrain',
            attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL'
        )
        
        # Add satellite layers
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri World Imagery',
            name='ESRI Satellite',
            overlay=False
        ).add_to(m)
        
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google Satellite',
            name='Google Satellite',
            overlay=False
        ).add_to(m)
        
        # Add grid cell
        cell_size = 0.01  # Approximately 1km at the equator
        bounds = [
            [latitude - cell_size/2, longitude - cell_size/2],
            [latitude + cell_size/2, longitude + cell_size/2]
        ]
        
        folium.Rectangle(
            bounds=bounds,
            color='red',
            weight=2,
            fill=False,
            popup=f'Grid Cell<br>Center: {latitude:.4f}, {longitude:.4f}'
        ).add_to(m)
        
        # Add center point marker
        folium.Marker(
            [latitude, longitude],
            popup=f'Center Point<br>Lat: {latitude}<br>Lon: {longitude}',
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m

def create_portfolio_map(coordinates):
    """Create a map showing all portfolio grid cells"""
    # Calculate center point of all coordinates
    center_lat = sum(lat for lat, _ in coordinates) / len(coordinates)
    center_lon = sum(lon for _, lon in coordinates) / len(coordinates)
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles='Stamen Terrain',
        attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL'
    )
    
    # Add satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery',
        name='Satellite',
        overlay=False
    ).add_to(m)
    
    # Add grid cells for each coordinate
    for lat, lon in coordinates:
        cell_size_km = 10
        lat_km = 111.0
        lon_km = 111.0 * np.cos(np.deg2rad(lat))
        
        cell_size_lat = cell_size_km / lat_km
        cell_size_lon = cell_size_km / lon_km
        
        start_lat = lat - (cell_size_lat / 2)
        start_lon = lon - (cell_size_lon / 2)
        end_lat = lat + (cell_size_lat / 2)
        end_lon = lon + (cell_size_lon / 2)
        
        bounds = [[start_lat, start_lon], [end_lat, end_lon]]
        
        folium.Rectangle(
            bounds=bounds,
            color='red',
            weight=2,
            fill=False,
            popup=f'Grid Cell<br>Center: {lat:.4f}, {lon:.4f}'
        ).add_to(m)
        
        folium.Marker(
            [lat, lon],
            popup=f'Center Point<br>Lat: {lat}<br>Lon: {lon}',
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    return m 

def get_satellite_imagery(latitude, longitude, start_date, end_date, dataset="VEGETATION"):
    """
    Get vegetation and land cover data from NASA POWER
    
    Parameters:
    latitude, longitude: coordinates
    start_date, end_date: datetime objects
    dataset: Type of data to retrieve (VEGETATION, LANDCOVER)
    """
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Parameters for vegetation analysis
    parameters = [
        "ALLSKY_SFC_PAR_TOT",  # Photosynthetically Active Radiation
        "ALLSKY_SFC_SW_DWN",   # Surface Solar Radiation
        "RH2M",                # Relative Humidity
        "T2M",                 # Temperature
        "PRECTOTCORR"         # Precipitation
    ]
    
    params = {
        "parameters": ",".join(parameters),
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date.strftime("%Y%m%d"),
        "end": end_date.strftime("%Y%m%d"),
        "format": "JSON"
    }
    
    try:
        print("Fetching data from NASA POWER...")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to time series
        dates = []
        values = []
        
        for date, measurements in data['properties']['parameter']['ALLSKY_SFC_PAR_TOT'].items():
            try:
                # Calculate vegetation index from available parameters
                par = float(data['properties']['parameter']['ALLSKY_SFC_PAR_TOT'][date])
                swr = float(data['properties']['parameter']['ALLSKY_SFC_SW_DWN'][date])
                rh = float(data['properties']['parameter']['RH2M'][date])
                temp = float(data['properties']['parameter']['T2M'][date])
                precip = float(data['properties']['parameter']['PRECTOTCORR'][date])
                
                # Simple vegetation index calculation
                # Higher values indicate better conditions for vegetation
                veg_index = (par * 0.3 + precip * 0.3 + rh * 0.2 + (20 - abs(temp - 20)) * 0.2) / 100
                
                dates.append(datetime.strptime(date, "%Y%m%d"))
                values.append(veg_index)
                
            except (ValueError, KeyError) as e:
                print(f"Skipping date {date}: {e}")
                continue
        
        if not dates:
            print("No valid data found")
            return None, None
            
        return dates, values
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None

def get_landsat_imagery(latitude, longitude, start_date, end_date):
    """Get Landsat satellite imagery time series using NASA's Earth API"""
    base_url = "https://api.nasa.gov/planetary/earth/assets"
    NASA_API_KEY = "lb3Y9J2USP4AyoOKnOe5Nb2eMcBDwyzodACPWtqN"  # Replace DEMO_KEY with your API key
    
    params = {
        "lat": latitude,
        "lon": longitude,
        "begin": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d"),
        "api_key": NASA_API_KEY,
        "dim": 0.1  # Roughly 1km at the equator
    }
    
    try:
        print("Fetching Landsat imagery...")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'results' not in data or not data['results']:
            print("No imagery available for the specified period")
            return None, None
        
        dates = []
        images = []
        
        for result in data['results']:
            try:
                img_date = datetime.strptime(result['date'], "%Y-%m-%d")
                img_url = result['url']
                
                # Get the image
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    img = Image.open(BytesIO(img_response.content))
                    images.append(img)
                    dates.append(img_date)
                    print(f"Retrieved image for {img_date.strftime('%Y-%m')}")
                
            except Exception as e:
                print(f"Error processing image: {e}")
                continue
                
        return dates, images
        
    except Exception as e:
        print(f"Error fetching Landsat data: {e}")
        return None, None

def create_temporal_grid_cell(latitude, longitude, start_date, end_date):
    """Create a grid cell visualization with temporal satellite imagery"""
    # Get vegetation data and Landsat imagery
    veg_dates, veg_values = get_satellite_imagery(latitude, longitude, start_date, end_date)
    img_dates, images = get_landsat_imagery(latitude, longitude, start_date, end_date)
    
    if not veg_dates or not veg_values:
        print("No vegetation data available")
        return None, None
    
    # Create visualization with more subplots
    fig = plt.figure(figsize=(15, 15))
    gs = plt.GridSpec(3, 2, figure=fig)
    
    # Plot 1: Vegetation Index Time Series
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(veg_dates, veg_values, 'g-', marker='o')
    ax1.set_title('Vegetation Conditions Index')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Index Value')
    ax1.grid(True)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Add trend line
    z = np.polyfit(mdates.date2num(veg_dates), veg_values, 1)
    p = np.poly1d(z)
    ax1.plot(veg_dates, p(mdates.date2num(veg_dates)), "r--", alpha=0.8, label='Trend')
    ax1.legend()
    
    # Plot 2: Monthly Distribution
    ax2 = fig.add_subplot(gs[1, 0])
    monthly_values = {}
    for date, value in zip(veg_dates, veg_values):
        month = date.strftime('%b')
        if month not in monthly_values:
            monthly_values[month] = []
        monthly_values[month].append(value)
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    box_data = [monthly_values.get(m, []) for m in months]
    
    ax2.boxplot(box_data, labels=months)
    ax2.set_title('Monthly Vegetation Conditions')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Index Value')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Landsat Image Time Series
    if images:
        # Create image grid
        n_images = len(images)
        rows = (n_images + 1) // 2  # Calculate needed rows
        
        for i, (date, img) in enumerate(zip(img_dates, images)):
            ax = fig.add_subplot(gs[1 + i//2, 1])
            ax.imshow(img)
            ax.set_title(date.strftime('%Y-%m'))
            ax.axis('off')
    
    # Create interactive map
    m = folium.Map(location=[latitude, longitude], zoom_start=12)
    
    # Add grid cell
    cell_size = 0.01
    bounds = [
        [latitude - cell_size/2, longitude - cell_size/2],
        [latitude + cell_size/2, longitude + cell_size/2]
    ]
    
    # Color based on current vegetation condition
    current_value = veg_values[-1]
    if current_value > 0.7:
        color = 'green'
    elif current_value > 0.4:
        color = 'yellow'
    else:
        color = 'red'
    
    folium.Rectangle(
        bounds=bounds,
        color=color,
        fill=True,
        popup=f'Grid Cell<br>Current Vegetation Index: {current_value:.2f}'
    ).add_to(m)
    
    # Add multiple satellite layers
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery',
        name='ESRI Satellite',
        overlay=False
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Google Satellite',
        overlay=False
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    # Save map
    map_filename = f"temp_map_{latitude}_{longitude}.html"
    m.save(map_filename)
    
    plt.tight_layout()
    return fig, map_filename

def plot_temporal_comparison(latitude, longitude, dates, values, metric="Vegetation Index"):
    """Create a temporal comparison visualization"""
    if not dates or not values:
        print(f"No {metric} data available")
        return None
        
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Time Series
    ax1.plot(dates, values, 'g-', marker='o')
    ax1.set_title(f'{metric} Time Series')
    ax1.set_xlabel('Date')
    ax1.set_ylabel(metric)
    ax1.grid(True)
    
    # Plot 2: Monthly Box Plot
    monthly_data = []
    month_labels = []
    
    for month in range(1, 13):
        month_values = [v for d, v in zip(dates, values) if d.month == month]
        if month_values:
            monthly_data.append(month_values)
            month_labels.append(datetime(2000, month, 1).strftime('%b'))
    
    if monthly_data:
        ax2.boxplot(monthly_data, labels=month_labels)
        ax2.set_title(f'Monthly {metric} Distribution')
        ax2.set_xlabel('Month')
        ax2.set_ylabel(metric)
        ax2.grid(True)
    
    plt.tight_layout()
    return fig 