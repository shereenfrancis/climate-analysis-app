import pandas as pd
import numpy as np
from scipy import stats

def calculate_trigger_levels(rainfall_data, percentiles=[10, 25, 50, 75, 90]):
    """Calculate trigger levels for parametric insurance"""
    monthly_triggers = {}
    for month in range(1, 13):
        month_data = rainfall_data[rainfall_data.index.month == month]['rainfall_mm']
        triggers = {}
        for p in percentiles:
            triggers[f'p{p}'] = np.percentile(month_data, p)
        monthly_triggers[month] = triggers
    return monthly_triggers

def calculate_risk_metrics(rainfall_data):
    """Calculate key risk metrics for underwriting"""
    metrics = {
        'volatility': rainfall_data['rainfall_mm'].std(),
        'skewness': stats.skew(rainfall_data['rainfall_mm']),
        'kurtosis': stats.kurtosis(rainfall_data['rainfall_mm']),
        'var_95': np.percentile(rainfall_data['rainfall_mm'], 5),  # Value at Risk
        'cvar_95': rainfall_data[rainfall_data['rainfall_mm'] <= np.percentile(rainfall_data['rainfall_mm'], 5)]['rainfall_mm'].mean(),  # Conditional VaR
        'max_consecutive_dry_months': calculate_consecutive_dry_months(rainfall_data),
        'drought_frequency': calculate_drought_frequency(rainfall_data),
        'seasonal_volatility': calculate_seasonal_volatility(rainfall_data)
    }
    return metrics

def calculate_consecutive_dry_months(rainfall_data, threshold_percentile=25):
    """Calculate maximum consecutive months below threshold"""
    threshold = np.percentile(rainfall_data['rainfall_mm'], threshold_percentile)
    dry_months = (rainfall_data['rainfall_mm'] < threshold).astype(int)
    return max_consecutive_ones(dry_months)

def max_consecutive_ones(binary_series):
    """Helper function to find maximum consecutive 1s in a series"""
    max_consecutive = 0
    current_consecutive = 0
    for value in binary_series:
        if value == 1:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0
    return max_consecutive

def calculate_drought_frequency(rainfall_data, threshold_percentile=25, window_years=5):
    """Calculate frequency of drought events over rolling periods"""
    threshold = np.percentile(rainfall_data['rainfall_mm'], threshold_percentile)
    drought_events = (rainfall_data['rainfall_mm'] < threshold).rolling(window=window_years*12).sum()
    return drought_events.mean() / (window_years*12)

def calculate_seasonal_volatility(rainfall_data):
    """Calculate volatility by season"""
    rainfall_data['season'] = pd.cut(rainfall_data.index.month, 
                                   bins=[0,3,6,9,12], 
                                   labels=['Summer', 'Autumn', 'Winter', 'Spring'])
    return rainfall_data.groupby('season')['rainfall_mm'].std().to_dict()

def simulate_payouts(rainfall_data, trigger_levels, payout_structure):
    """Simulate insurance payouts based on trigger levels"""
    payouts = []
    for index, row in rainfall_data.iterrows():
        month = index.month
        rainfall = row['rainfall_mm']
        monthly_triggers = trigger_levels[month]
        
        # Calculate payout based on trigger levels
        if rainfall <= monthly_triggers['p10']:
            payouts.append(payout_structure['severe'])
        elif rainfall <= monthly_triggers['p25']:
            payouts.append(payout_structure['moderate'])
        elif rainfall <= monthly_triggers['p50']:
            payouts.append(payout_structure['mild'])
        else:
            payouts.append(0)
            
    return pd.Series(payouts, index=rainfall_data.index) 