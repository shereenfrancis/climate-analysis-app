import pandas as pd
import numpy as np
from scipy import stats

def calculate_climate_metrics(rainfall_data):
    """Calculate key climate risk metrics"""
    
    # Basic rainfall statistics
    metrics = {
        'annual_average': rainfall_data['rainfall_mm'].mean() * 12,  # Annualized
        'monthly_variability': rainfall_data['rainfall_mm'].std(),
        'coefficient_variation': rainfall_data['rainfall_mm'].std() / rainfall_data['rainfall_mm'].mean(),
        
        # Extreme events
        'dry_months_per_year': (rainfall_data['rainfall_mm'] < rainfall_data['rainfall_mm'].quantile(0.1)).mean() * 12,
        'wet_months_per_year': (rainfall_data['rainfall_mm'] > rainfall_data['rainfall_mm'].quantile(0.9)).mean() * 12,
        
        # Seasonal patterns
        'seasonal_reliability': calculate_seasonal_reliability(rainfall_data),
        'growing_season_rainfall': calculate_growing_season_rainfall(rainfall_data),
        
        # Trend analysis
        'rainfall_trend': calculate_rainfall_trend(rainfall_data),
        
        # Risk indicators
        'drought_risk_score': calculate_drought_risk(rainfall_data),
        'seasonal_predictability': calculate_seasonal_predictability(rainfall_data)
    }
    
    return metrics

def calculate_seasonal_reliability(rainfall_data):
    """Calculate reliability of seasonal rainfall patterns"""
    seasonal = rainfall_data.groupby([rainfall_data.index.year, rainfall_data.index.month])['rainfall_mm'].sum()
    cv_by_month = seasonal.groupby(level=1).std() / seasonal.groupby(level=1).mean()
    return cv_by_month.mean()  # Lower is more reliable

def calculate_growing_season_rainfall(rainfall_data, growing_months=[10,11,12,1,2,3]):
    """Calculate statistics for the main growing season"""
    growing_season = rainfall_data[rainfall_data.index.month.isin(growing_months)]
    return {
        'total': growing_season['rainfall_mm'].sum(),
        'reliability': growing_season['rainfall_mm'].std() / growing_season['rainfall_mm'].mean(),
        'early_season': growing_season[growing_season.index.month.isin([10,11])]['rainfall_mm'].mean(),
        'mid_season': growing_season[growing_season.index.month.isin([12,1])]['rainfall_mm'].mean(),
        'late_season': growing_season[growing_season.index.month.isin([2,3])]['rainfall_mm'].mean()
    }

def calculate_rainfall_trend(rainfall_data):
    """Calculate long-term rainfall trends"""
    years = rainfall_data.index.year - rainfall_data.index.year[0]
    slope, _, r_value, p_value, _ = stats.linregress(years, rainfall_data['rainfall_mm'])
    return {
        'trend_mm_per_year': slope * 12,  # Annualized trend
        'significance': p_value,
        'r_squared': r_value**2
    }

def calculate_drought_risk(rainfall_data):
    """Calculate drought risk indicators"""
    monthly_mean = rainfall_data['rainfall_mm'].mean()
    drought_threshold = monthly_mean * 0.6  # 60% of average
    
    consecutive_dry = 0
    max_consecutive = 0
    dry_spells = []
    
    for value in rainfall_data['rainfall_mm']:
        if value < drought_threshold:
            consecutive_dry += 1
        else:
            max_consecutive = max(max_consecutive, consecutive_dry)
            if consecutive_dry > 0:
                dry_spells.append(consecutive_dry)
            consecutive_dry = 0
    
    return {
        'max_consecutive_dry': max_consecutive,
        'avg_dry_spell': np.mean(dry_spells) if dry_spells else 0,
        'dry_spell_frequency': len(dry_spells) / len(rainfall_data) * 12  # Annual frequency
    }

def calculate_seasonal_predictability(rainfall_data):
    """Calculate how predictable seasonal patterns are"""
    monthly_avg = rainfall_data.groupby(rainfall_data.index.month)['rainfall_mm'].mean()
    monthly_std = rainfall_data.groupby(rainfall_data.index.month)['rainfall_mm'].std()
    
    return {
        'seasonality_index': (monthly_avg.max() - monthly_avg.min()) / monthly_avg.mean(),
        'month_to_month_variation': monthly_avg.diff().std(),
        'seasonal_timing_consistency': monthly_std.mean() / monthly_avg.mean()
    } 