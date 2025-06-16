import os
import pandas as pd
import numpy as np
import re

# Define the smallest time step to filter the data (used for downsampling)
TIME_STEP = 5e-07
# Tolerance for floating point comparison (to avoid precision errors)
TOLERANCE = 1e-10

# Get the current working directory where the script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
print("Current working directory:", current_dir)

i = 1
# Iterate over each file in the current directory
for filename in os.listdir(current_dir):
    if filename.endswith(".csv"):
        try:
            i = i + 1
            # Load the CSV file into a DataFrame
            file_path = os.path.join(current_dir, filename)
            df = pd.read_csv(file_path)

            # Check if the necessary columns are present
            required_columns = ['Time', 'Iout', "IGBT Leg1.PWM_Modulator.TOP_1", 'IGBT Leg1.PWM_Modulator.BOT_1']
            if not all(col in df.columns for col in required_columns):
                print(f"Skipping {filename}: required columns not found.")
                continue

            # Keep only the relevant columns for analysis
            df = df[required_columns]

            # Filter rows where 'Time' is approximately a multiple of the defined TIME_STEP
            df_filtered = df[np.abs((df['Time'] / TIME_STEP).round() - (df['Time'] / TIME_STEP)) < TOLERANCE]

            # Reset the index after filtering
            df_filtered.reset_index(drop=True, inplace=True)

            # Add a constant time step column for reference
            df_filtered['time_step'] = TIME_STEP

            # Extract the inductance value 'L' from the filename using a regular expression
            match = re.search(r"L=(?P<L>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", filename)
            if match:
                L_val = match.group("L")
                # Sanitize the extracted value to avoid illegal filename characters
                safe_L_val = re.sub(r'[\\/*?:"<>|]', "_", L_val)
                print("Extracted L:", L_val)
                print("Safe L:", safe_L_val)

            # Add the extracted L value as a column to the DataFrame
            df_filtered['L_value'] = safe_L_val

            # Compute the next value of current for each row
            df_filtered['next_value'] = df_filtered['Iout'].shift(-1)

            # Remove the last row which will have NaN in the 'next_value' column
            df_filtered.dropna(inplace=True)

            # Rename columns to standard names for further processing or ML training
            df_filtered.rename(columns={
                'Time': 'time',
                'Iout': 'value',
                "IGBT Leg1.PWM_Modulator.TOP_1": 'top',
                'IGBT Leg1.PWM_Modulator.BOT_1': 'bot'
            }, inplace=True)

            # Extract the base name (without extension) from the filename
            base_name, _ = os.path.splitext(filename)

            # Create a new filename to save the processed DataFrame
            new_filename = f"new_{base_name}_time_step_5e-7.csv"
            df_filtered.to_csv(os.path.join(current_dir, new_filename), index=False)

            print(f"Processed file: {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
