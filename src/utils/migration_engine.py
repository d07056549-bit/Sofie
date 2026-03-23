import pandas as pd
import numpy as np

class MigrationEngine:
    def __init__(self, data_path="Data/raw/Migration & Refugee Flows/"):
        self.path = data_path

    def get_displacement_risk(self):
        try:
            # Load the main time series
            df = pd.read_csv(f"{self.path}time_series.csv", low_memory=False)
            
            # Filter for most recent available historical data
            latest_year = df['Year'].max()
            current_data = df[df['Year'] == latest_year].copy() # Added .copy() to prevent warnings
            
            # 1. Clean the 'Value' column
            # Convert '*' to 1, others to numeric, and force to FLOAT
            current_data.loc[:, 'Value'] = pd.to_numeric(
                current_data['Value'].astype(str).replace('\*', '1', regex=True), 
                errors='coerce'
            ).fillna(0).astype(float)
            
            # 2. Aggregate 'Value' by Country of Origin
            displacement_stats = current_data.groupby('Origin')['Value'].sum().reset_index()
            displacement_stats.columns = ['COUNTRY', 'DISPLACEMENT_VOL']
            
            # 3. FORCE FLOAT TYPE BEFORE MATH (Crucial for the ufunc error)
            vol_array = displacement_stats['DISPLACEMENT_VOL'].values.astype(float)
            
            # 4. Normalize score 0-1 (Log scale)
            displacement_stats['DISPLACEMENT_SCORE'] = np.log1p(vol_array)
            
            max_score = displacement_stats['DISPLACEMENT_SCORE'].max()
            if max_score > 0:
                displacement_stats['DISPLACEMENT_SCORE'] = (displacement_stats['DISPLACEMENT_SCORE'] / max_score)
            else:
                displacement_stats['DISPLACEMENT_SCORE'] = 0.0
            
            return displacement_stats.set_index('COUNTRY')['DISPLACEMENT_SCORE'].to_dict()
            
        except Exception as e:
            print(f"⚠️ Migration Engine Offline: {e}")
            return {}
