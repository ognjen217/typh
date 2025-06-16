import os
import pandas as pd
import numpy as np
import re
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
            if not all(col in df.columns for col in ['Time','Ia',"Ib",'Ic','Inv1.Phase A.PWM_Modulator.TOP_1','Inv1.Phase A.PWM_Modulator.BOT_1',"Inv1.Phase B.PWM_Modulator.TOP_1","Inv1.Phase B.PWM_Modulator.BOT_1","Inv1.Phase C.PWM_Modulator.TOP_1",'Inv1.Phase C.PWM_Modulator.BOT_1']):
                print(f"Skipping {filename}: required columns not found.")
                continue

            # Zadrži samo kolone koje su nam potrebne
            df = df[['Time','Ia',"Ib",'Ic','Inv1.Phase A.PWM_Modulator.TOP_1','Inv1.Phase A.PWM_Modulator.BOT_1',"Inv1.Phase B.PWM_Modulator.TOP_1","Inv1.Phase B.PWM_Modulator.BOT_1","Inv1.Phase C.PWM_Modulator.TOP_1",'Inv1.Phase C.PWM_Modulator.BOT_1']]

            # Filtriraj redove gde je Time višekratnik od 1e-5
            df_filtered = df[np.abs((df['Time'] / TIME_STEP).round() - (df['Time'] / TIME_STEP)) < TOLERANCE]

            # Resetuj indekse
            df_filtered.reset_index(drop=True, inplace=True)

            match = re.search(r"L=(?P<L>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", filename)

            if match:
                L_val = match.group("L")
                safe_L_val = re.sub(r'[\\/*?:"<>|]', "_", L_val)  # replace illegal filename chars
                print("Extracted L:", L_val)
                print("Safe L:", safe_L_val)

            df_filtered['La_value'] = 1e-2
            df_filtered['Lb_value'] = 1e-3
            df_filtered['Lc_value'] = 1e-5

            # Dodaj next_time i next_value
            df_filtered['time_step'] = 5e-7
            df_filtered['Ia_next_value'] = df_filtered['Ia'].shift(-1)
            df_filtered['Ib_next_value'] = df_filtered['Ib'].shift(-1)
            df_filtered['Ic_next_value'] = df_filtered['Ic'].shift(-1)
            
            # Ukloni poslednji red (jer ima NaN u next_* kolonama)
            df_filtered.dropna(inplace=True)

            # Preimenuj kolone za izlaz
            df_filtered.rename(columns={
                'Time': 'time',
                'Iout': 'value',
                "Inv1.Phase A.PWM_Modulator.TOP_1" : 'topA', 
                'Inv1.Phase A.PWM_Modulator.BOT_1' : 'botA',
                "Inv1.Phase B.PWM_Modulator.TOP_1" : "topB",
                'Inv1.Phase B.PWM_Modulator.BOT_1' : 'botB',
                "Inv1.Phase C.PWM_Modulator.TOP_1" : "topC",
                'Inv1.Phase C.PWM_Modulator.BOT_1' : 'botC'

            }, inplace=True)
            base_name, _ = os.path.splitext(filename)
            
            # Sačuvaj rezultat
            new_filename = f"new_{base_name}_time_step_5e-7.csv"
            df_filtered.to_csv(os.path.join(current_dir, new_filename), index=False)

            print(f"Processed file: {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")