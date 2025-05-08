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

st.set_page_config(page_title="Climate Analysis", layout="wide")

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
                # Plot soil moisture
                fig = plot_soil_moisture(soil_df, latitude, longitude)
                st.pyplot(fig)
                
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
                    temp_metrics = climate_df[temp_cols].describe()
                    st.dataframe(temp_metrics.round(2))
                    
                    st.write("### Moisture and Humidity")
                    moisture_cols = ["PRECTOTCORR", "RH2M", "QV2M"]
                    moisture_metrics = climate_df[moisture_cols].describe()
                    st.dataframe(moisture_metrics.round(2))
                    
                    st.write("### Wind Conditions")
                    wind_cols = ["WS2M", "WS10M", "WS50M"]
                    wind_metrics = climate_df[wind_cols].describe()
                    st.dataframe(wind_metrics.round(2))
                    
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