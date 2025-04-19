import pandas as pd
from datetime import datetime

# Load the CSV file
input_file = 'BTCUSDT.csv'
output_file = 'BTCUSDT_2020_2025.csv'

# Read the CSV file
df = pd.read_csv(input_file)

# Convert the datetime column to datetime type
df['datetime'] = pd.to_datetime(df['datetime'])

# Filter data between 2020-01-01 and 2025-01-01
start_date = datetime(2020, 1, 1)
end_date = datetime(2025, 1, 1)
filtered_df = df[(df['datetime'] >= start_date) & (df['datetime'] < end_date)]

# Save the filtered data to a new CSV file
filtered_df.to_csv(output_file, index=False)

print(f"Original data shape: {df.shape}")
print(f"Filtered data shape: {filtered_df.shape}")
print(f"Filtered data saved to {output_file}")