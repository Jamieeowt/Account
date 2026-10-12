import pandas as pd
import numpy as np

#Load the raw dataset
df = pd.read_csv('philippines_tourism_data (2).csv')

#Pre-clean strings in numerical columns (e.g., extracting numbers from 'PHP 25087')
df['AvgSpendingPHP'] = df['AvgSpendingPHP'].astype(str).str.replace(r'[^\d.-]', '', regex=True)

#Force Number Columns to be Numbers
df['AvgSpendingPHP'] = pd.to_numeric(df['AvgSpendingPHP'], errors='coerce')
df['SatisfactionRating'] = pd.to_numeric(df['SatisfactionRating'], errors='coerce')
df['AvgStayDays'] = pd.to_numeric(df['AvgStayDays'], errors='coerce')
df['NumberOfVisitors'] = pd.to_numeric(df['NumberOfVisitors'], errors='coerce')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

# Fixing the Negative Numbers Turning Them Positive
num_cols = ['AvgSpendingPHP', 'SatisfactionRating', 'AvgStayDays', 'NumberOfVisitors']
for col in num_cols:
    df[col] = df[col].abs()

# Cap Satisfaction Rating at 5.0 and scale down rogue entries > 5
df['SatisfactionRating'] = df['SatisfactionRating'].apply(lambda x: x / 2 if pd.notnull(x) and x > 5 else x)
df['SatisfactionRating'] = df['SatisfactionRating'].clip(0, 5.0)

#Handle Missing Numerical Data
df['AvgSpendingPHP'] = df['AvgSpendingPHP'].fillna(df['AvgSpendingPHP'].median())
if df['SatisfactionRating'].isnull().any():
    df['SatisfactionRating'] = df['SatisfactionRating'].fillna(df['SatisfactionRating'].mean())
df['AvgStayDays'] = df['AvgStayDays'].fillna(df['AvgStayDays'].median())
df['NumberOfVisitors'] = df['NumberOfVisitors'].fillna(df['NumberOfVisitors'].median())
df['Year'] = df['Year'].fillna(df['Year'].median())

# Round floating point columns for cleaner presentation
df['SatisfactionRating'] = df['SatisfactionRating'].round(1)
df['AvgSpendingPHP'] = df['AvgSpendingPHP'].round(0)
df['AvgStayDays'] = df['AvgStayDays'].round(1)

#Fill Missing Text
text_cols_to_fill = ['Season', 'VisitPurpose', 'Accommodation', 'Month']
for col in text_cols_to_fill:
    if col in df.columns:
        df[col] = df[col].fillna('Unknown')

#Standardize Text Formatting
text_columns = ['Destination', 'Province', 'IslandGroup', 'Season', 'TouristOrigin', 'VisitPurpose', 'Accommodation', 'Month']
for col in text_columns:
    if col in df.columns:
        # Apply string ops only to non-null to avoid 'Nan' string
        mask = df[col].notna()
        # In Pandas 3.x, to avoid type assignment errors when converting mixed types to string, 
        # we can just convert the whole column to object/string first if it's not already.
        df[col] = df[col].astype(str)
        df.loc[mask, col] = df.loc[mask, col].str.strip().str.title().str.replace(r'\s+', ' ', regex=True)
        # Fix 'Nan' string from astype(str) where it was initially null
        df[col] = df[col].replace('Nan', 'Unknown')

#Fix specific inconsistencies in categorical columns
df['Destination'] = df['Destination'].replace({'Cebu': 'Cebu City', 'Davao': 'Davao City', 'Boracay Island': 'Boracay'})
df['Province'] = df['Province'].str.replace('Del Sur', 'del Sur').str.replace('Del Norte', 'del Norte')

origin_mapping = {
    'U.S.A.': 'USA',
    'United States': 'USA',
    'Us': 'USA',
    'Usa': 'USA',
    'England': 'UK',
    'U.K.': 'UK',
    'Uk': 'UK',
    'United Kingdom': 'UK',
    'Korea': 'South Korea',
    'S. Korea': 'South Korea'
}
df['TouristOrigin'] = df['TouristOrigin'].replace(origin_mapping)

#Remove Duplicates
df = df.drop_duplicates()

#Save Clean Data
df.to_csv('cleaned_philippines_tourism_data.csv', index=False)
print("Data is now 100% clean, with no negative numbers, properly formatted cities, and capped ratings!")