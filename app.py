import streamlit as st
import pandas as pd
from rainfall_analysis import get_monthly_rainfall_analysis, plot_rainfall_analysis, get_summary_statistics
from soil_moisture_analysis import get_soil_moisture_data, plot_soil_moisture, get_soil_moisture_stats
from location_utils import get_location_info
from mapping_utils import (
    create_single_grid_cell, 
    create_portfolio_map, 
    get_satellite_imagery,
    plot_temporal_comparison,
    create_temporal_grid_cell
)
from insurance_utils import (calculate_trigger_levels, calculate_risk_metrics, simulate_payouts)
from climate_metrics import calculate_climate_metrics
import matplotlib.pyplot as plt
from visualization_utils import (
    plot_monthly_distribution, 
    plot_rainfall_heatmap, 
    plot_cumulative_rainfall, 
    plot_drought_analysis, 
    plot_seasonal_patterns,
    plot_location_comparison,
    plot_seasonal_comparison,
    plot_interactive_soil_moisture
)
from climate_data_analysis import get_nasa_power_data, plot_climate_data, analyze_temperature
from datetime import datetime, timedelta

def show_location_analysis(lat, lon, title="Location Analysis"):
    """Helper function to show analysis for a single location"""
    location = get_location_info(lat, lon)
    
    st.subheader(f"{title} ({lat:.2f}, {lon:.2f})")
    col1, col2 = st.columns(2)
    col1.metric("Province", location["province"])
    col2.metric("District", location["district"])
    
    monthly_df = get_monthly_rainfall_analysis(lat, lon)
    if monthly_df is not None:
        stats = get_summary_statistics(monthly_df)
        
        # Calculate standard deviation and CV directly from the data
        std_monthly = monthly_df['rainfall_mm'].std()
        cv = std_monthly / stats['avg_monthly'] if stats['avg_monthly'] > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Annual Average Rainfall", f"{stats['avg_monthly']*12:.0f} mm")
        col2.metric("Monthly Variability", f"{stats['max_monthly'] - stats['min_monthly']:.1f} mm")
        col3.metric("Coefficient of Variation", f"{cv:.2f}")
        
        # Add CV and std to stats dictionary for use in comparison
        stats['cv'] = cv
        stats['std_monthly'] = std_monthly
        
        return monthly_df, stats
    return None, None

# Password check must come before ANY other st commands
def check_password():
    """Returns `True` if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.text_input(
            "Enter the password to access the app", 
            type="password", 
            key="password",
            on_change=password_entered
        )
        st.write("Contact administrator for access.")
        return False
    
    return st.session_state["password_correct"]

def password_entered():
    """Checks whether a password entered by the user is correct."""
    if st.session_state["password"] == st.secrets["password"]:
        st.session_state["password_correct"] = True
    else:
        st.session_state["password_correct"] = False
        st.error("😕 Password incorrect")

# Check password before ANY other Streamlit commands
if not check_password():
    st.stop()

# Only after password check, do page config and other setup
st.set_page_config(
    page_title="Climate Analysis Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with climate theme
st.markdown("""
<style>
    /* Main background and text */
    .main {
        background-color: #1a1a1a !important;  /* Dark background */
        color: #ffffff;  /* White text */
    }
    
    /* All containers and cards */
    .element-container, .stMarkdown, div[data-testid="stVerticalBlock"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Input fields */
    .stNumberInput, .stTextInput, .stDateInput {
        background-color: #2C3E50 !important;
        color: white !important;
        border-radius: 5px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2E86C1;  /* Ocean blue */
        color: white !important;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #21618C;
        transform: translateY(-2px);
    }
    
    /* Metrics */
    .stMetric {
        background-color: #2C3E50 !important;  /* Dark blue-grey */
        color: white !important;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #2E86C1;
        margin: 10px 0;
    }
    
    .stMetric > div {
        color: white !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #3498DB !important;  /* Bright blue */
    }
    
    h1 {
        text-align: center;
        padding: 20px;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    h2 {
        border-bottom: 3px solid #3498DB;
        padding-bottom: 8px;
        margin-top: 30px;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #2C3E50 !important;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #34495E !important;
        border-radius: 5px;
        padding: 10px 16px;
        color: white !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2E86C1 !important;
        color: white !important;
    }
    
    /* DataFrames */
    .dataframe {
        background-color: #2C3E50 !important;
        color: white !important;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Radio buttons and checkboxes */
    .stRadio > label, .stCheckbox > label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess {
        background-color: rgba(47, 173, 102, 0.2) !important;
        color: #2FAD66 !important;
    }
    
    .stWarning {
        background-color: rgba(247, 183, 49, 0.2) !important;
        color: #F7B731 !important;
    }
    
    .stError {
        background-color: rgba(231, 76, 60, 0.2) !important;
        color: #E74C3C !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #3498DB !important;
    }
    
    /* Progress bar */
    .stProgress > div {
        background-color: #2E86C1 !important;
    }
    
    /* Text elements */
    .stText, p, span {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Only after password check, do all other imports and setup
from location_utils import get_location_info
from mapping_utils import (
    create_single_grid_cell, 
    create_portfolio_map, 
    get_satellite_imagery,
    plot_temporal_comparison,
    create_temporal_grid_cell
)
from insurance_utils import (calculate_trigger_levels, calculate_risk_metrics, 
                           simulate_payouts)
from climate_metrics import calculate_climate_metrics
import matplotlib.pyplot as plt
from visualization_utils import plot_monthly_distribution, plot_rainfall_heatmap, plot_cumulative_rainfall, plot_drought_analysis, plot_seasonal_patterns
from climate_data_analysis import get_nasa_power_data, plot_climate_data, analyze_temperature
from datetime import datetime, timedelta

# Define the portfolio coordinates
PORTFOLIO_COORDINATES = [
    (-24.35, 29.15), (-24.45, 29.05), (-24.45, 29.15), (-24.45, 29.25),
    (-24.55, 29.05), (-24.85, 28.65), (-24.85, 28.75), (-25.55, 29.75),
    # ... add all coordinates here ...
    (-28.15, 26.65), (-28.15, 27.75), (-28.15, 29.05)
]

st.title("Climate Analysis Dashboard")

# Create tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Custom Coordinates", "Portfolio Analysis", 
    "Soil Moisture Analysis", "Map View",
    "Climate Risk Analysis"
])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input("Enter Latitude", value=-26.45, min_value=-90.0, max_value=90.0)
    with col2:
        longitude = st.number_input("Enter Longitude", value=29.65, min_value=-180.0, max_value=180.0)

    if st.button("Analyze Custom Location"):
        with st.spinner("Fetching and analyzing rainfall data..."):
            # Get location information
            location = get_location_info(latitude, longitude)
            
            # Display location information
            st.subheader("Location Information")
            col1, col2 = st.columns(2)
            col1.metric("Province", location["province"])
            col2.metric("District", location["district"])
            
            monthly_df = get_monthly_rainfall_analysis(latitude, longitude)
            if monthly_df is not None:
                fig = plot_rainfall_analysis(monthly_df, latitude, longitude)
                st.pyplot(fig)
                
                stats = get_summary_statistics(monthly_df)
                
                st.subheader("Summary Statistics")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Average Monthly Rainfall", f"{stats['avg_monthly']:.1f} mm")
                col2.metric("Maximum Monthly Rainfall", f"{stats['max_monthly']:.1f} mm")
                col3.metric("Minimum Monthly Rainfall", f"{stats['min_monthly']:.1f} mm")
                col4.metric("Total Years of Data", stats['total_years'])
                
                st.subheader("Seasonal Averages")
                for season, avg in stats['seasonal_avg'].items():
                    st.metric(season, f"{avg:.1f} mm")
                
                csv = monthly_df.to_csv()
                st.download_button(
                    label="Download Data as CSV",
                    data=csv,
                    file_name=f"rainfall_timeseries_{latitude}_{longitude}_to_july2024.csv",
                    mime="text/csv"
                )

with tab2:
    st.subheader("Portfolio Analysis")
    
    # Create a formatted display of coordinates for selection
    coordinate_options = [f"{lat}, {lon}" for lat, lon in PORTFOLIO_COORDINATES]
    selected_coordinate = st.selectbox(
        "Select Grid Cell Coordinates",
        options=coordinate_options,
        format_func=lambda x: f"Latitude: {x.split(',')[0]}, Longitude: {x.split(',')[1]}"
    )
    
    if st.button("Analyze Portfolio Location"):
        # Parse selected coordinates
        lat, lon = map(float, selected_coordinate.split(','))
        
        with st.spinner("Fetching and analyzing rainfall data..."):
            # Get location information
            location = get_location_info(lat, lon)
            
            # Display location information
            st.subheader("Location Information")
            col1, col2 = st.columns(2)
            col1.metric("Province", location["province"])
            col2.metric("District", location["district"])
            
            monthly_df = get_monthly_rainfall_analysis(lat, lon)
            if monthly_df is not None:
                fig = plot_rainfall_analysis(monthly_df, lat, lon)
                st.pyplot(fig)
                
                stats = get_summary_statistics(monthly_df)
                
                st.subheader("Summary Statistics")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Average Monthly Rainfall", f"{stats['avg_monthly']:.1f} mm")
                col2.metric("Maximum Monthly Rainfall", f"{stats['max_monthly']:.1f} mm")
                col3.metric("Minimum Monthly Rainfall", f"{stats['min_monthly']:.1f} mm")
                col4.metric("Total Years of Data", stats['total_years'])
                
                st.subheader("Seasonal Averages")
                for season, avg in stats['seasonal_avg'].items():
                    st.metric(season, f"{avg:.1f} mm")
                
                csv = monthly_df.to_csv()
                st.download_button(
                    label="Download Data as CSV",
                    data=csv,
                    file_name=f"rainfall_timeseries_{lat}_{lon}_to_july2024.csv",
                    mime="text/csv"
                )

    # Optional: Add a feature to analyze all portfolio locations
    if st.button("Analyze All Portfolio Locations"):
        st.write("This will take some time to process all locations...")
        
        # Create a progress bar
        progress_bar = st.progress(0)
        
        for i, (lat, lon) in enumerate(PORTFOLIO_COORDINATES):
            # Update progress
            progress = (i + 1) / len(PORTFOLIO_COORDINATES)
            progress_bar.progress(progress)
            
            # Get location information
            location = get_location_info(lat, lon)
            
            st.subheader(f"Analysis for Latitude: {lat}, Longitude: {lon}")
            col1, col2 = st.columns(2)
            col1.metric("Province", location["province"])
            col2.metric("District", location["district"])
            
            monthly_df = get_monthly_rainfall_analysis(lat, lon)
            
            if monthly_df is not None:
                fig = plot_rainfall_analysis(monthly_df, lat, lon)
                st.pyplot(fig)
                
                stats = get_summary_statistics(monthly_df)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Average Monthly Rainfall", f"{stats['avg_monthly']:.1f} mm")
                col2.metric("Maximum Monthly Rainfall", f"{stats['max_monthly']:.1f} mm")
                col3.metric("Minimum Monthly Rainfall", f"{stats['min_monthly']:.1f} mm")
                col4.metric("Total Years of Data", stats['total_years'])

with tab3:
    st.subheader("Soil Moisture Analysis")
    
    # Add data source information
    with st.expander("ℹ️ About the Data"):
        st.markdown("""
        **Data Source: NASA POWER (Prediction Of Worldwide Energy Resources)**
        
        This analysis uses NASA's satellite-derived soil moisture data:
        
        **Measurements:**
        - **Profile Soil Moisture**: Average moisture through entire soil profile (0-200cm depth)
        - **Root Zone Moisture**: Critical zone for plant water uptake (0-100cm depth)
        - **Surface Soil Moisture**: Top layer moisture content (0-5cm depth)
        
        **Technical Details:**
        - Values shown in m³/m³ (volumetric water content)
        - Daily measurements
        - Spatial resolution: 0.5° x 0.5° grid
        - Data source: power.larc.nasa.gov
        
        **Interactive Features:**
        - Toggle different soil layers
        - Zoom and pan through time
        - View 7-day moving averages
        - Compare moisture levels across depths
        """)
    
    analysis_type = st.radio(
        "Choose Analysis Type",
        ["Custom Location", "Portfolio Location"],
        key="soil_moisture_analysis_type"
    )
    
    if analysis_type == "Custom Location":
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Enter Latitude", value=-26.45, min_value=-90.0, max_value=90.0, key="soil_lat")
        with col2:
            longitude = st.number_input("Enter Longitude", value=29.65, min_value=-180.0, max_value=180.0, key="soil_lon")
            
    else:
        coordinate_options = [f"{lat}, {lon}" for lat, lon in PORTFOLIO_COORDINATES]
        selected_coordinate = st.selectbox(
            "Select Grid Cell Coordinates",
            options=coordinate_options,
            format_func=lambda x: f"Latitude: {x.split(',')[0]}, Longitude: {x.split(',')[1]}"
        )
        latitude, longitude = map(float, selected_coordinate.split(','))
    
    if st.button("Analyze Soil Moisture"):
        with st.spinner("Fetching and analyzing soil moisture data..."):
            # Get location information
            location = get_location_info(latitude, longitude)
            
            # Display location information
            st.subheader("Location Information")
            col1, col2 = st.columns(2)
            col1.metric("Province", location["province"])
            col2.metric("District", location["district"])
            
            # Get and plot soil moisture data
            soil_df = get_soil_moisture_data(latitude, longitude)
            
            if soil_df is not None:
                # Original static plot
                st.write("### Traditional Plot")
                fig = plot_soil_moisture(soil_df, latitude, longitude)
                st.pyplot(fig)
                
                # New interactive plot
                st.write("### Interactive Soil Moisture Analysis")
                interactive_fig = plot_interactive_soil_moisture(soil_df, latitude, longitude)
                st.plotly_chart(interactive_fig, use_container_width=True)
                
                # Display statistics
                stats = get_soil_moisture_stats(soil_df)
                
                st.subheader("Soil Moisture Statistics")
                
                for moisture_type, values in stats.items():
                    st.write(f"\n{moisture_type}:")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Average", f"{values['mean']:.1f}%")
                    col2.metric("Maximum", f"{values['max']:.1f}%")
                    col3.metric("Minimum", f"{values['min']:.1f}%")
                
                # Add download button for CSV
                csv = soil_df.to_csv()
                st.download_button(
                    label="Download Soil Moisture Data as CSV",
                    data=csv,
                    file_name=f"soil_moisture_{latitude}_{longitude}_to_july2024.csv",
                    mime="text/csv"
                )
            else:
                st.error("Error fetching soil moisture data. Please try again.")

# Add new tab for mapping
with tab4:
    st.subheader("Map Visualization")
    
    view_type = st.radio(
        "Choose View Type",
        ["Single Location", "Portfolio View", "Temporal Analysis"]
    )
    
    if view_type == "Single Location":
        col1, col2 = st.columns(2)
        with col1:
            map_lat = st.number_input("Enter Latitude", value=-26.45, min_value=-90.0, max_value=90.0, key="map_lat")
        with col2:
            map_lon = st.number_input("Enter Longitude", value=29.65, min_value=-180.0, max_value=180.0, key="map_lon")
        
        if st.button("Show Grid Cell"):
            # Create map for single location
            m = create_single_grid_cell(map_lat, map_lon)
            
            # Get location info
            location = get_location_info(map_lat, map_lon)
            
            # Display location information
            col1, col2 = st.columns(2)
            col1.metric("Province", location["province"])
            col2.metric("District", location["district"])
            
            # Display the map
            st.components.v1.html(m._repr_html_(), height=600)
            
    elif view_type == "Portfolio View":
        if st.button("Show Portfolio Grid Cells"):
            # Create map for all portfolio locations
            m = create_portfolio_map(PORTFOLIO_COORDINATES)
            
            # Display the map
            st.components.v1.html(m._repr_html_(), height=600)
            
            # Display summary
            st.write(f"Total number of grid cells: {len(PORTFOLIO_COORDINATES)}")
            
            # Optional: Display list of coordinates with province/district
            if st.checkbox("Show Grid Cell Details"):
                st.write("Grid Cell Information:")
                for lat, lon in PORTFOLIO_COORDINATES:
                    location = get_location_info(lat, lon)
                    st.write(f"Coordinates: {lat}, {lon}")
                    st.write(f"Province: {location['province']}")
                    st.write(f"District: {location['district']}")
                    st.write("---")
    elif view_type == "Temporal Analysis":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            latitude = st.number_input("Enter Latitude", value=-26.45)
        with col2:
            longitude = st.number_input("Enter Longitude", value=29.65)
        with col3:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
        with col4:
            end_date = st.date_input("End Date", value=datetime.now())
            
        if st.button("Analyze Temporal Data"):
            with st.spinner("Fetching satellite data..."):
                fig, map_file = create_temporal_grid_cell(
                    latitude, longitude, 
                    start_date=start_date,
                    end_date=end_date
                )
                
                if fig:
                    st.pyplot(fig)
                    st.components.v1.html(open(map_file).read(), height=500)
                    
                    # Get vegetation health index
                    st.write("### Vegetation Health Analysis")
                    dates, vhi_values = get_satellite_imagery(
                        latitude, longitude, 
                        start_date, end_date,
                        dataset="MODIS_Terra_NDVI"  # Using NDVI for vegetation health
                    )
                    if dates and vhi_values:
                        vhi_fig = plot_temporal_comparison(
                            latitude, longitude,
                            dates, vhi_values,
                            metric="Vegetation Health Index"
                        )
                        st.pyplot(vhi_fig)
                    else:
                        st.warning("No vegetation health data available for the specified period")
                else:
                    st.warning("Could not fetch satellite imagery. Showing static map instead.")

# Add new climate risk analysis tab
with tab5:
    st.subheader("Climate Risk Analysis")
    
    # Add comparison mode toggle
    comparison_mode = st.checkbox("Enable Location Comparison", key="comparison_mode")
    
    if comparison_mode:
        st.write("### Compare Two Locations")
        
        # First location
        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Location 1")
            lat1 = st.number_input("Latitude 1", value=-26.45, min_value=-90.0, max_value=90.0, key="lat1")
            lon1 = st.number_input("Longitude 1", value=29.65, min_value=-180.0, max_value=180.0, key="lon1")
            
        with col2:
            st.write("#### Location 2")
            lat2 = st.number_input("Latitude 2", value=-24.35, min_value=-90.0, max_value=90.0, key="lat2")
            lon2 = st.number_input("Longitude 2", value=29.15, min_value=-180.0, max_value=180.0, key="lon2")
        
        if st.button("Compare Locations"):
            with st.spinner("Analyzing both locations..."):
                # Analyze first location
                col1, col2 = st.columns(2)
                with col1:
                    df1, stats1 = show_location_analysis(lat1, lon1, "Location 1")
                
                with col2:
                    df2, stats2 = show_location_analysis(lat2, lon2, "Location 2")
                
                if df1 is not None and df2 is not None:
                    st.write("### Comparative Analysis")
                    
                    # Calculate differences
                    rainfall_diff = stats1['avg_monthly']*12 - stats2['avg_monthly']*12  # Annual rainfall
                    variability_diff = (stats1['max_monthly'] - stats1['min_monthly']) - (stats2['max_monthly'] - stats2['min_monthly'])
                    
                    # Show differences
                    col1, col2 = st.columns(2)
                    col1.metric(
                        "Rainfall Difference",
                        f"{abs(rainfall_diff):.0f} mm",
                        f"Location 1 is {'higher' if rainfall_diff > 0 else 'lower'}"
                    )
                    col2.metric(
                        "Variability Difference",
                        f"{abs(variability_diff):.1f} mm",
                        f"Location 1 is {'more variable' if variability_diff > 0 else 'less variable'}"
                    )
                    
                    # Plot comparative visualizations
                    st.write("### Rainfall Pattern Comparison")
                    comparison_fig = plot_location_comparison(df1, df2, lat1, lon1, lat2, lon2)
                    st.pyplot(comparison_fig)
                    
                    # Add seasonal comparison
                    st.write("### Seasonal Comparison")
                    seasonal_comp_fig = plot_seasonal_comparison(df1, df2, lat1, lon1, lat2, lon2)
                    st.pyplot(seasonal_comp_fig)
    
    else:
        analysis_type = st.radio(
            "Choose Analysis Type",
            ["Custom Location", "Portfolio Location"],
            key="climate_risk_analysis_type"
        )
        
        if analysis_type == "Custom Location":
            col1, col2 = st.columns(2)
            with col1:
                clim_lat = st.number_input("Enter Latitude", value=-26.45, min_value=-90.0, max_value=90.0, key="clim_lat")
            with col2:
                clim_lon = st.number_input("Enter Longitude", value=29.65, min_value=-180.0, max_value=180.0, key="clim_lon")
        else:
            coordinate_options = [f"{lat}, {lon}" for lat, lon in PORTFOLIO_COORDINATES]
            selected_coordinate = st.selectbox(
                "Select Grid Cell Coordinates",
                options=coordinate_options,
                format_func=lambda x: f"Latitude: {x.split(',')[0]}, Longitude: {x.split(',')[1]}",
                key="clim_coords"
            )
            clim_lat, clim_lon = map(float, selected_coordinate.split(','))

        if st.button("Analyze Climate Risk"):
            with st.spinner("Analyzing climate risk patterns..."):
                monthly_df = get_monthly_rainfall_analysis(clim_lat, clim_lon)
                
                if monthly_df is not None:
                    metrics = calculate_climate_metrics(monthly_df)
                    
                    # Display basic climate statistics
                    st.subheader("Rainfall Patterns")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Annual Average Rainfall", f"{metrics['annual_average']:.0f} mm")
                    col2.metric("Monthly Variability", f"{metrics['monthly_variability']:.1f} mm")
                    col3.metric("Coefficient of Variation", f"{metrics['coefficient_variation']:.2f}")
                    
                    # Display growing season analysis
                    st.subheader("Growing Season Analysis")
                    growing = metrics['growing_season_rainfall']
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Early Season Rainfall", f"{growing['early_season']:.1f} mm")
                    col2.metric("Mid Season Rainfall", f"{growing['mid_season']:.1f} mm")
                    col3.metric("Late Season Rainfall", f"{growing['late_season']:.1f} mm")
                    
                    # Display trend analysis
                    st.subheader("Long-term Trends")
                    trend = metrics['rainfall_trend']
                    col1, col2 = st.columns(2)
                    col1.metric("Annual Rainfall Trend", 
                              f"{trend['trend_mm_per_year']:.1f} mm/year",
                              delta="Increasing" if trend['trend_mm_per_year'] > 0 else "Decreasing")
                    col2.metric("Trend Confidence", 
                              f"{(1 - trend['significance']) * 100:.1f}%")
                    
                    # Display drought risk indicators
                    st.subheader("Drought Risk Indicators")
                    drought = metrics['drought_risk_score']
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Max Consecutive Dry Months", f"{drought['max_consecutive_dry']}")
                    col2.metric("Average Dry Spell Length", f"{drought['avg_dry_spell']:.1f} months")
                    col3.metric("Annual Dry Spell Frequency", f"{drought['dry_spell_frequency']:.1f}")
                    
                    # Display seasonal predictability
                    st.subheader("Seasonal Patterns")
                    seasonal = metrics['seasonal_predictability']
                    col1, col2 = st.columns(2)
                    col1.metric("Seasonality Index", f"{seasonal['seasonality_index']:.2f}")
                    col2.metric("Seasonal Timing Consistency", 
                              f"{seasonal['seasonal_timing_consistency']:.2f}")
                    
                    # Add visualizations
                    st.subheader("Rainfall Distribution Analysis")
                    dist_fig = plot_monthly_distribution(monthly_df)
                    st.pyplot(dist_fig)
                    
                    st.subheader("Rainfall Patterns Heatmap")
                    heat_fig = plot_rainfall_heatmap(monthly_df)
                    st.pyplot(heat_fig)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Cumulative Rainfall Analysis")
                        cum_fig = plot_cumulative_rainfall(monthly_df)
                        st.pyplot(cum_fig)
                    
                    with col2:
                        st.subheader("Drought Period Analysis")
                        drought_fig = plot_drought_analysis(monthly_df)
                        st.pyplot(drought_fig)
                    
                    st.subheader("Seasonal Pattern Analysis")
                    season_fig = plot_seasonal_patterns(monthly_df)
                    st.pyplot(season_fig)
                    
                    # Optional: Download detailed report
                    if st.button("Generate Detailed Report"):
                        report = generate_detailed_report(monthly_df, metrics)
                        st.download_button(
                            label="Download Detailed Climate Risk Report",
                            data=report,
                            file_name=f"climate_risk_report_{clim_lat}_{clim_lon}.pdf",
                            mime="application/pdf"
                        )

                    st.subheader("Comprehensive Climate Analysis")
                    
                    # Fetch comprehensive climate data
                    daily_df, climate_df = get_nasa_power_data(clim_lat, clim_lon)
                    
                    if climate_df is not None:
                        # Group metrics by category
                        st.write("### Temperature Metrics")
                        temp_cols = ["T2M", "T2M_MAX", "T2M_MIN", "T2MDEW"]
                        available_temp_cols = [col for col in temp_cols if col in climate_df.columns]
                        if available_temp_cols:
                            temp_metrics = climate_df[available_temp_cols].describe()
                            st.dataframe(temp_metrics.round(2))
                        else:
                            st.warning("Temperature metrics not available")

                        st.write("### Moisture and Humidity")
                        # Updated column names based on NASA POWER API
                        moisture_cols = [
                            "PRECTOT",  # Total precipitation
                            "RH2M",     # Relative humidity
                            "QV2M",     # Specific humidity
                            "GWETPROF", # Soil moisture
                            "GWETROOT"  # Root zone soil wetness
                        ]
                        available_moisture_cols = [col for col in moisture_cols if col in climate_df.columns]
                        if available_moisture_cols:
                            moisture_metrics = climate_df[available_moisture_cols].describe()
                            st.dataframe(moisture_metrics.round(2))
                        else:
                            st.warning("Moisture and humidity metrics not available")

                        st.write("### Wind Conditions")
                        wind_cols = ["WS2M", "WS10M", "WS50M"]
                        available_wind_cols = [col for col in wind_cols if col in climate_df.columns]
                        if available_wind_cols:
                            wind_metrics = climate_df[available_wind_cols].describe()
                            st.dataframe(wind_metrics.round(2))
                        else:
                            st.warning("Wind metrics not available")

                        # Add column information
                        with st.expander("📊 Data Column Descriptions"):
                            st.markdown("""
                            **Temperature Metrics:**
                            - T2M: Temperature at 2 meters (°C)
                            - T2M_MAX: Maximum temperature at 2 meters (°C)
                            - T2M_MIN: Minimum temperature at 2 meters (°C)
                            - T2MDEW: Dew point temperature at 2 meters (°C)
                            
                            **Moisture and Humidity:**
                            - PRECTOT: Total precipitation (mm/day)
                            - RH2M: Relative humidity at 2 meters (%)
                            - QV2M: Specific humidity at 2 meters (g/kg)
                            - GWETPROF: Soil moisture profile (%)
                            - GWETROOT: Root zone soil wetness (%)
                            
                            **Wind Conditions:**
                            - WS2M: Wind speed at 2 meters (m/s)
                            - WS10M: Wind speed at 10 meters (m/s)
                            - WS50M: Wind speed at 50 meters (m/s)
                            """)

                        # Debug information
                        if st.checkbox("Show Debug Information"):
                            st.write("Available columns in the dataset:", climate_df.columns.tolist())

                        # Plot climate parameters
                        st.write("### Climate Parameter Trends")
                        climate_fig = plot_climate_data(climate_df, clim_lat, clim_lon)
                        st.pyplot(climate_fig)
                        
                        # Seasonal analysis
                        st.write("### Seasonal Patterns")
                        climate_df['season'] = pd.cut(climate_df.index.month, 
                                                    bins=[0,3,6,9,12], 
                                                    labels=['Summer', 'Autumn', 'Winter', 'Spring'])
                        seasonal_avg = climate_df.groupby('season').mean()
                        st.dataframe(seasonal_avg.round(2))
                        
                        # Download option
                        csv = climate_df.to_csv()
                        st.download_button(
                            label="Download Complete Climate Data",
                            data=csv,
                            file_name=f"climate_data_{clim_lat}_{clim_lon}.csv",
                            mime="text/csv"
                        )

                        if 'T2M' in daily_df.columns:  # Use daily_df for temperature analysis
                            st.subheader("Detailed Temperature Analysis")
                            
                            # Get temperature analysis
                            temp_analysis = analyze_temperature(daily_df)
                            
                            if temp_analysis is not None:  # Check if analysis was successful
                                # Display key temperature metrics
                                st.write("### Temperature Overview")
                                col1, col2, col3, col4 = st.columns(4)
                                
                                col1.metric("Average Temperature", 
                                          f"{temp_analysis['stats']['mean_temp']:.1f}°C")
                                col2.metric("All-time Maximum", 
                                          f"{temp_analysis['stats']['max_temp_ever']:.1f}°C")
                                col3.metric("All-time Minimum", 
                                          f"{temp_analysis['stats']['min_temp_ever']:.1f}°C")
                                col4.metric("Average Daily Range", 
                                          f"{temp_analysis['stats']['diurnal_range']:.1f}°C")
                                
                                # Display risk metrics
                                st.write("### Temperature Risk Indicators")
                                col1, col2, col3 = st.columns(3)
                                
                                col1.metric("Days Above 30°C", 
                                          temp_analysis['stats']['days_above_30'])
                                col2.metric("Days Below 0°C", 
                                          temp_analysis['stats']['days_below_0'])
                                col3.metric("Frost Risk Days", 
                                          temp_analysis['stats']['frost_risk_days'])
                                
                                # Display temperature trends
                                st.write("### Temperature Trends")
                                st.pyplot(temp_analysis['trend_fig'])
                                
                                # Display monthly patterns
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("### Monthly Temperature Distribution")
                                    st.pyplot(temp_analysis['monthly_fig'])
                                
                                with col2:
                                    st.write("### Temperature Patterns by Year")
                                    st.pyplot(temp_analysis['heat_fig'])
                                
                                # Display monthly statistics
                                st.write("### Detailed Monthly Statistics")
                                st.dataframe(temp_analysis['monthly'].round(2))
                                
                                # Display day/night analysis
                                st.write("### Day vs Night Temperature Analysis")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.metric("Average Day Temperature", 
                                            f"{temp_analysis['stats']['avg_day_temp']:.1f}°C")
                                    st.metric("Very Hot Days (>35°C)", 
                                            temp_analysis['stats']['extreme_hot_days'])
                                
                                with col2:
                                    st.metric("Average Night Temperature", 
                                            f"{temp_analysis['stats']['avg_night_temp']:.1f}°C")
                                    st.metric("Very Cold Nights (<5°C)", 
                                            temp_analysis['stats']['extreme_cold_nights'])
                                
                                # Display day/night patterns
                                st.pyplot(temp_analysis['daynight_fig'])
                                
                                # Display monthly day/night statistics
                                st.write("### Monthly Day/Night Temperature Patterns")
                                st.dataframe(temp_analysis['daynight_stats'].round(1))
                                
                                # Add interpretation
                                st.write("""
                                ### Day/Night Temperature Analysis
                                
                                - **Daily Range**: The location experiences an average daily temperature 
                                  range of {:.1f}°C between day and night.
                                - **Daytime Patterns**: Average daytime temperatures reach {:.1f}°C, 
                                  with {} days exceeding 35°C annually.
                                - **Nighttime Patterns**: Average nighttime temperatures drop to {:.1f}°C, 
                                  with {} nights below 5°C annually.
                                - **Seasonal Variation**: The greatest day-night temperature difference 
                                  occurs in {}, while the smallest occurs in {}.
                                """.format(
                                    temp_analysis['stats']['diurnal_range'],
                                    temp_analysis['stats']['avg_day_temp'],
                                    temp_analysis['stats']['extreme_hot_days'],
                                    temp_analysis['stats']['avg_night_temp'],
                                    temp_analysis['stats']['extreme_cold_nights'],
                                    temp_analysis['daynight_stats']['temp_range'].idxmax(),
                                    temp_analysis['daynight_stats']['temp_range'].idxmin()
                                ))

                                st.write("### Year-by-Year Temperature Comparison")
                                st.pyplot(temp_analysis['yearly_comparison_fig'])
                                
                                st.write("### Seasonal Temperature Patterns")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.pyplot(temp_analysis['seasonal_comparison_fig'])
                                
                                with col2:
                                    st.write("#### Seasonal Statistics")
                                    st.dataframe(temp_analysis['seasonal_stats'])
                                    
                                    # Add seasonal interpretation
                                    warmest_season = temp_analysis['seasonal_stats']['avg_day_temp'].idxmax()
                                    coldest_season = temp_analysis['seasonal_stats']['avg_day_temp'].idxmin()
                                    most_variable = temp_analysis['seasonal_stats']['std_day_temp'].idxmax()
                                    
                                    st.write(f"""
                                    - Warmest season: **{warmest_season}** (avg: {temp_analysis['seasonal_stats'].loc[warmest_season, 'avg_day_temp']:.1f}°C)
                                    - Coldest season: **{coldest_season}** (avg: {temp_analysis['seasonal_stats'].loc[coldest_season, 'avg_day_temp']:.1f}°C)
                                    - Most variable: **{most_variable}** (std: {temp_analysis['seasonal_stats'].loc[most_variable, 'std_day_temp']:.1f}°C)
                                    """)

def show_location_analysis(lat, lon, title="Location Analysis"):
    """Helper function to show analysis for a single location"""
    location = get_location_info(lat, lon)
    
    st.subheader(f"{title} ({lat:.2f}, {lon:.2f})")
    col1, col2 = st.columns(2)
    col1.metric("Province", location["province"])
    col2.metric("District", location["district"])
    
    monthly_df = get_monthly_rainfall_analysis(lat, lon)
    if monthly_df is not None:
        stats = get_summary_statistics(monthly_df)
        
        # Calculate standard deviation and CV directly from the data
        std_monthly = monthly_df['rainfall_mm'].std()
        cv = std_monthly / stats['avg_monthly'] if stats['avg_monthly'] > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Annual Average Rainfall", f"{stats['avg_monthly']*12:.0f} mm")
        col2.metric("Monthly Variability", f"{stats['max_monthly'] - stats['min_monthly']:.1f} mm")
        col3.metric("Coefficient of Variation", f"{cv:.2f}")
        
        # Add CV and std to stats dictionary for use in comparison
        stats['cv'] = cv
        stats['std_monthly'] = std_monthly
        
        return monthly_df, stats
    return None, None 