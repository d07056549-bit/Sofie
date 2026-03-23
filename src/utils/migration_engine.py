import pandas as pd
import numpy as np

class MigrationEngine:
    def __init__(self, data_path="Data/raw/Migration & Refugee Flows/"):
        self.path = data_path

    def get_displacement_risk(self):
        try:
            # Load the main time series
            df = pd.read_csv(f"{self.path}time_series.csv", low_memory=False)
            
            # Filter for most recent available historical data (e.g., 2016) 
            # as a baseline for 2026 projections
            latest_year = df['Year'].max()
            current_data = df[df['Year'] == latest_year]
            
            # Aggregate 'Value' by Country of Origin
            # Converting '*' to 1 (minimal) and others to numeric
            current_data.loc[:, 'Value'] = pd.to_numeric(current_data['Value'].replace('*', 1), errors='coerce').fillna(0)
            
            displacement_stats = current_data.groupby('Origin')['Value'].sum().reset_index()
            displacement_stats.columns = ['COUNTRY', 'DISPLACEMENT_VOL']
            
            # Normalize score 0-1 (Log scale because displacement numbers vary wildly)
            displacement_stats['DISPLACEMENT_SCORE'] = np.log1p(displacement_stats['DISPLACEMENT_VOL'])
            max_score = displacement_stats['DISPLACEMENT_SCORE'].max()
            displacement_stats['DISPLACEMENT_SCORE'] = (displacement_stats['DISPLACEMENT_SCORE'] / max_score)
            
            return displacement_stats.set_index('COUNTRY')['DISPLACEMENT_SCORE'].to_dict()
        except Exception as e:
            print(f"⚠️ Migration Engine Offline: {e}")
            return {}
