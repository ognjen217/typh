import os
import pandas as pd
import numpy as np

# Definiši najmanji vremenski korak (1e-5)
TIME_STEP = 5e-07
TOLERANCE = 1e-10  # tolerancija zbog floating point preciznosti

# Trenutni direktorijum
current_dir = os.path.dirname(os.path.abspath(__file__))
print("Current working directory:", current_dir)


for filename in os.listdir(current_dir):
    if filename.endswith(".csv"):
        try:
            # Učitaj fajl
            file_path = os.path.join(current_dir, filename)
            df = pd.read_csv(file_path)

            # Provera zaglavlja
            if not all(col in df.columns for col in ['Time', 'Iout', "IGBT Leg1.PWM_Modulator.TOP_1", 'IGBT Leg1.PWM_Modulator.BOT_1']):
                print(f"Skipping {filename}: required columns not found.")
                continue

            # Zadrži samo kolone koje su nam potrebne
            df = df[['Time', 'Iout', "IGBT Leg1.PWM_Modulator.TOP_1", 'IGBT Leg1.PWM_Modulator.BOT_1']]

            # Filtriraj redove gde je Time višekratnik od 1e-5
            df_filtered = df[np.abs((df['Time'] / TIME_STEP).round() - (df['Time'] / TIME_STEP)) < TOLERANCE]

            # Resetuj indekse
            df_filtered.reset_index(drop=True, inplace=True)

            # Dodaj next_time i next_value
            df_filtered['time_step'] = 5e-7
            df_filtered['next_value'] = df_filtered['Iout'].shift(-1)
            # Ukloni poslednji red (jer ima NaN u next_* kolonama)
            df_filtered.dropna(inplace=True)

            # Preimenuj kolone za izlaz
            df_filtered.rename(columns={
                'Time': 'time',
                'Iout': 'value',
                "IGBT Leg1.PWM_Modulator.TOP_1" : 'top', 
                'IGBT Leg1.PWM_Modulator.BOT_1' : 'bot'
            }, inplace=True)
            base_name, _ = os.path.splitext(filename)
            
            # Sačuvaj rezultat
            new_filename = f"new_{base_name}_time_step_5e-7.csv"
            df_filtered.to_csv(os.path.join(current_dir, new_filename), index=False)

            print(f"Processed file: {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")