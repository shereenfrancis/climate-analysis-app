import pandas as pd
import numpy as np
from scipy import stats

def calculate_trigger_levels(data, percentiles=[10, 25, 50, 75, 90]):
    """Calculate trigger levels based on historical data"""
    triggers = {}
    for p in percentiles:
        triggers[f'p{p}'] = np.percentile(data, p)
    return triggers

def calculate_risk_metrics(data, trigger_level):
    """Calculate basic risk metrics"""
    below_trigger = data < trigger_level
    frequency = below_trigger.mean()
    severity = (trigger_level - data[below_trigger]).mean() if any(below_trigger) else 0
    
    return {
        'frequency': frequency,
        'severity': severity,
        'expected_loss': frequency * severity
    }

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

def simulate_payouts(data, trigger_level, payout_per_unit=1.0):
    """Simulate insurance payouts"""
    payouts = np.zeros_like(data)
    below_trigger = data < trigger_level
    payouts[below_trigger] = (trigger_level - data[below_trigger]) * payout_per_unit
    
    return {
        'payouts': payouts,
        'total_payout': payouts.sum(),
        'avg_annual_payout': payouts.mean(),
        'max_payout': payouts.max(),
        'payout_frequency': (payouts > 0).mean()
    } 