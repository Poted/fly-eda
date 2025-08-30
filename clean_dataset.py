import pandas as pd
import numpy as np
import re
from datetime import datetime


def convert_duration_to_float(duration_str):
    if isinstance(duration_str, str):
        match = re.search(r'(\d+)h\s*(\d+)m', duration_str)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            return round(hours + minutes / 60, 2)
    return np.nan

def convert_time_to_category(time_str):
    try:
        if isinstance(time_str, str):
            hour = int(time_str.split(':')[0])
            if 4 <= hour < 8:
                return 'Early_Morning'
            elif 8 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 16:
                return 'Afternoon'
            elif 16 <= hour < 20:
                return 'Evening'
            else:
                return 'Night'
        return time_str
    except (ValueError, IndexError):
        return np.nan

def create_clean_dataset(business_file, economy_file, output_file, today):

    try:
        df_business = pd.read_csv(business_file)
        df_economy = pd.read_csv(economy_file)

        df_business['class'] = 'Business'
        df_economy['class'] = 'Economy'

        df_combined = pd.concat([df_business, df_economy], ignore_index=True)

        for col in df_combined.select_dtypes(include=['object']).columns:
            df_combined[col] = df_combined[col].str.strip()

        df_combined['flight'] = df_combined['ch_code'].astype(str) + '-' + df_combined['num_code'].astype(str)

        df_combined = df_combined.rename(columns={
            'from': 'source_city',
            'to': 'destination_city',
            'dep_time': 'departure_time',
            'arr_time': 'arrival_time'
        })

        df_combined['stops'] = df_combined['stop']  
        df_combined['duration'] = df_combined['time_taken'].apply(convert_duration_to_float)

        df_combined['departure_time'] = df_combined['departure_time'].apply(convert_time_to_category)
        df_combined['arrival_time'] = df_combined['arrival_time'].apply(convert_time_to_category)

        df_combined['price'] = df_combined['price'].astype(str).str.replace(',', '', regex=False).astype(float).astype(int)

        reference_date = datetime.strptime(today, '%d-%m-%Y')
        df_combined['date'] = pd.to_datetime(df_combined['date'], format='%d-%m-%Y')
        df_combined['days_left'] = (df_combined['date'] - reference_date).dt.days

        final_df = df_combined[[
            'airline',
            'flight',
            'source_city',
            'departure_time',
            'stops',
            'arrival_time',
            'destination_city',
            'class',
            'duration',
            'days_left',
            'price'
        ]].copy()

        final_df.dropna(inplace=True)
        
        final_df.sort_values(by=['days_left', 'price'], inplace=True)
        
        final_df.insert(0, 'id', range(len(final_df)))
        final_df.rename(columns={'id': ''}, inplace=True)

        final_df.to_csv(output_file, index=False)
        print(f"Successfully created '{output_file}' with {len(final_df)} rows.")

    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    business_csv = 'data/buisness.csv'
    economy_csv = 'data/economy.csv'
    output_csv = 'data/clean_dataset.csv'
    today = '10-02-2022'
    create_clean_dataset(business_csv, economy_csv, output_csv, today)
