# 🔌 Half-Bridge IGBT Leg Modeling with Physics-Informed Neural Networks

This repository contains training and evaluation scripts for modeling current evolution in a half-bridge IGBT circuit using a neural network augmented with physics-informed loss terms.

---

## 📁 Repository Structure

```
.
├── half_bridge_model_full_training.ipynb   # Main training script (Jupyter Notebook)
├── half_bridge_model_test_script.ipynb     # Testing and evaluation script
├── *.csv                                   # Input simulation data files
```

---

## 🧰 Requirements

To run the scripts, install the following Python packages:

```bash
pip install torch numpy pandas matplotlib scikit-learn
```

We recommend using Python 3.8+ and a GPU-enabled PyTorch build for training speed.

---

## 📄 Input Files

Example input `.csv` files provided:

- `igbt_leg_L=1e-6.csv`
- `igbt_leg_L=2e-3.csv`
- `igbt_leg_L=2e-2.csv`
- `3_ph_igbt_leg_La=1e-2_Lb=1e-3_Lc=1e-5.csv`
- `3_ph_igbt_leg_La=2e-3_Lb=3e-6_Lc=6e-4.csv`

These files should contain the following columns (in order):

```
time, value, top, bot, time_step, L_value, next_value
```


---
## 📂 get_files_ready(): File Pattern Helper

This utility function helps automate the discovery and filtering of `.csv` input files based on phase configuration and sampling resolution.

### 🔧 Function Signature
```python
get_files_ready(phases=1, time_step=5e-7)
```

### 🧠 Parameters:
- `phases`: `int`  
  Indicates the number of system phases.  
  - `1` → Single-phase file filtering  
  - `3` → Looks for three-phase CSV filenames
- `time_step`: `float`  
  Filters files based on desired sampling interval embedded in the filename (e.g. `_time_step_5e-7`)

### ✅ Behavior:
- Scans the current working directory (not relying on `__file__`).
- Filters CSV files with names that match expected patterns:
  - For single-phase: looks for filenames like `igbt_leg_L=*`
  - For three-phase: looks for filenames like `3_ph_igbt_leg*`
  - Filters further by matching the `time_step` substring

### 🧪 Example Usage
```python
files = get_files_ready(phases=1, time_step=5e-7)
print("Found files:", files)
```

You can then use the returned list to instantiate the dataset:
```python
dataset = TimeSeriesDataset(files)
```

### 📌 Note:
This function is useful in automated pipelines where filenames encode important simulation parameters such as inductance values and time step size.

---

## 🚀 How to Run Training

1. Open `half_bridge_model_full_training.ipynb` in Jupyter or Google Colab.
2. Ensure your `.csv` data files are in the same directory.
3. Execute the notebook cells step-by-step to:
   - Load and preprocess the data
   - Define the model
   - Train using K-Fold cross-validation
   - Save the trained model

The output model will be saved as a `.pth` file (PyTorch state dictionary).

---

## ✅ How to Run Evaluation/Test

1. Open `half_bridge_model_test_script.ipynb`.
2. Set your desired test CSV file in the relevant cell, e.g.:

```python
test_file = "3_ph_igbt_leg_La=1e-2_Lb=1e-3_Lc=1e-5.csv"
```

3. Run all cells. The notebook will:
   - Load the trained model
   - Perform autoregressive prediction
   - Plot predicted vs actual current
   - Compute and display error metrics (MAE, RMSE, etc.)

---

## 📊 Example Output

The evaluation notebook will generate:

- 📈 Time-series plots comparing predictions and ground truth
- 📉 Error metrics (e.g., MAE, relative error per step)

---

## ✍️ Author & Notes

Developed by Ognjen Peric.  
For issues or collaboration requests, please open an issue on the repository.


