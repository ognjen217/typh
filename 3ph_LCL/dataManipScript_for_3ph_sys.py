import os
import pandas as pd
import numpy as np
import re

TIME_STEP = 5e-07
TOLERANCE = 1e-10

# Ako koristiš Jupyter ili pokrećeš direktno: koristi getcwd()
current_dir = os.getcwd()
print("Current working directory:", current_dir)

for filename in os.listdir(current_dir):
    if filename.endswith(".csv"):
        try:
            file_path = os.path.join(current_dir, filename)
            df = pd.read_csv(file_path)

            required_columns = [
                'Time', 'Ia', 'Ib', 'Ic',
                'Inv1.Phase A.PWM_Modulator.TOP_1', 'Inv1.Phase A.PWM_Modulator.BOT_1',
                'Inv1.Phase B.PWM_Modulator.TOP_1', 'Inv1.Phase B.PWM_Modulator.BOT_1',
                'Inv1.Phase C.PWM_Modulator.TOP_1', 'Inv1.Phase C.PWM_Modulator.BOT_1'
            ]

            if not all(col in df.columns for col in required_columns):
                print(f"⚠️ Skipping {filename}: required columns not found.")
                continue

            df = df[required_columns]
            df_filtered = df[np.abs((df['Time'] / TIME_STEP).round() - (df['Time'] / TIME_STEP)) < TOLERANCE]
            df_filtered.reset_index(drop=True, inplace=True)

            # Parsiranje parametara
            param_names = ['La', 'Lb', 'Lc', 'Lag', 'Lbg', 'Lcg', 'Ca', 'Cb', 'Cc', 'L', 'Lg', 'C']
            pattern = r'(?P<name>' + '|'.join(param_names) + r')=(?P<val>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)'
            matches = re.findall(pattern, filename)
            param_values = {name: float(val) for name, val in matches}

            # Dodaj parametre u dataframe
            df_filtered["La_value"]  = param_values.get("La", param_values.get("L", 1e-4))
            df_filtered["Lb_value"]  = param_values.get("Lb", param_values.get("L", 1e-4))
            df_filtered["Lc_value"]  = param_values.get("Lc", param_values.get("L", 1e-4))
            df_filtered["Lag_value"] = param_values.get("Lag", param_values.get("Lg", 1e-4))
            df_filtered["Lbg_value"] = param_values.get("Lbg", param_values.get("Lg", 1e-4))
            df_filtered["Lcg_value"] = param_values.get("Lcg", param_values.get("Lg", 1e-4))
            df_filtered["Ca_value"]  = param_values.get("Ca", param_values.get("C", 1e-4))
            df_filtered["Cb_value"]  = param_values.get("Cb", param_values.get("C", 1e-4))
            df_filtered["Cc_value"]  = param_values.get("Cc", param_values.get("C", 1e-4))
            df_filtered["time_step"] = TIME_STEP

            # Dodaj naredne vrednosti
            df_filtered["Ia_next_value"] = df_filtered["Ia"].shift(-1)
            df_filtered["Ib_next_value"] = df_filtered["Ib"].shift(-1)
            df_filtered["Ic_next_value"] = df_filtered["Ic"].shift(-1)
            df_filtered.dropna(inplace=True)

            # Preimenuj kolone
            df_filtered.rename(columns={
                'Time': 'time',
                'Inv1.Phase A.PWM_Modulator.TOP_1': 'topA',
                'Inv1.Phase A.PWM_Modulator.BOT_1': 'botA',
                'Inv1.Phase B.PWM_Modulator.TOP_1': 'topB',
                'Inv1.Phase B.PWM_Modulator.BOT_1': 'botB',
                'Inv1.Phase C.PWM_Modulator.TOP_1': 'topC',
                'Inv1.Phase C.PWM_Modulator.BOT_1': 'botC'
            }, inplace=True)

            base_name, _ = os.path.splitext(filename)
            new_filename = f"new_{base_name}_time_step_{TIME_STEP:.0e}.csv"
            df_filtered.to_csv(os.path.join(current_dir, new_filename), index=False)

            print(f"✅ Processed file: {filename}")

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
