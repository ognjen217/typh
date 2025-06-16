import os
import pandas as pd
import numpy as np

# Definiši najmanji vremenski korak (1e-5)
TIME_STEP = 20e-5
TOLERANCE = 1e-10  # tolerancija zbog floating point preciznosti

# Trenutni direktorijum
current_dir = os.path.dirname(os.path.abspath(__file__))
print("Current working directory:", current_dir)


for filename in os.listdir(current_dir):
    if filename.endswith(".csv") and filename.startswith("data") and not ("time" in filename and "_step_" in filename):
        try:
            # Učitaj fajl
            file_path = os.path.join(current_dir, filename)
            df = pd.read_csv(file_path)

            # Provera zaglavlja
            if not all(col in df.columns for col in ['Time', 'Va2']):
                print(f"Skipping {filename}: required columns not found.")
                continue

            # Zadrži samo kolone koje su nam potrebne
            df = df[['Time', 'Va2']]

            # Filtriraj redove gde je Time višekratnik od 1e-5
            df_filtered = df[np.abs((df['Time'] / TIME_STEP).round() - (df['Time'] / TIME_STEP)) < TOLERANCE]

            # Resetuj indekse
            df_filtered.reset_index(drop=True, inplace=True)

            # Dodaj next_time i next_value
            df_filtered['next_time'] = df_filtered['Time'].shift(-1)
            df_filtered['next_value'] = df_filtered['Va2'].shift(-1)

            # Ukloni poslednji red (jer ima NaN u next_* kolonama)
            df_filtered.dropna(inplace=True)

            # Preimenuj kolone za izlaz
            df_filtered.rename(columns={
                'Time': 'time',
                'Va2': 'value'
            }, inplace=True)

            # Sačuvaj rezultat
            new_filename = f"filtered_modified_{filename}_time_step_{'20e-5'}.csv"
            df_filtered.to_csv(os.path.join(current_dir, new_filename), index=False)

            print(f"Processed file: {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")