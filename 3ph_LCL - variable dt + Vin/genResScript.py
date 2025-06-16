import os
from pathlib import Path
import pytest
from typhoon.api import hil
from typhoon.api.schematic_editor import model
import typhoon.test.reporting.messages as report
import typhoon.api.hil as hil
from typhoon.test import capture
import pandas as pd
import numpy as np
import math

# Script directory
FILE_DIR_PATH = Path(__file__).resolve().parent

# Path to model file and compiled model file
MODEL_PATH = FILE_DIR_PATH / "3ph_inv_lcl.tse" 
COMPILED_MODEL_PATH = model.get_compiled_model_file(MODEL_PATH)


# Define the lists of cutoff frequencies and capacitances
L_values   = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
Lg_values  = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
C_values   = [1e-6, 1e-5, 1e-4, 1e-3      ]
Vin_values = [100,  200,  300,  400, 500  ]

@pytest.fixture(scope="module", params=C_values)
def _C_values(request):    
    return request.param

@pytest.fixture(scope="module", params=Vin_values)
def _Vin_values(request):    
    return request.param

@pytest.fixture(scope="module", params=L_values)
def _L_values(request):    
    return request.param

@pytest.fixture(scope="module", params=Lg_values)
def _Lg_values(request):
    return request.param
    

'''_C_values, _R_values'''

@pytest.fixture(scope="module")
def setup_control(_C_values, _L_values, _Lg_values, _Vin_values):    
    model.load(MODEL_PATH)    
    # set properties    
    C   =  _C_values
    L   =  _L_values
    Lg  =  _Lg_values
    Vin =  _Vin_values
    model.set_component_property("Ca",  "capacitance",  C )   
    model.set_component_property("Cc",  "capacitance",  C )
    model.set_component_property("Cb",  "capacitance",  C )
    model.set_component_property("La",  "inductance" ,  L )
    model.set_component_property("Lb",  "inductance" ,  L )
    model.set_component_property("Lc",  "inductance" ,  L )
    model.set_component_property("Lag", "inductance"          ,  Lg)
    model.set_component_property("Lbg", "inductance"          ,  Lg)
    model.set_component_property("Lcg", "inductance"          ,  Lg)
    model.set_component_property("Vin", "init_const_value"    , Vin)
    
    # compile schematic and load it to hil/vhil device    
    model.compile(conditional_compile=True)    
    hil.load_model(COMPILED_MODEL_PATH, vhil_device=True)    

    return L, C, Lg, Vin


def test_rectifier(setup_control):
    """
    Test the system response for disturbance rejection with different R and C values.
    """
    L  = setup_control[0]
    C  = setup_control[1]
    Lg = setup_control[2]
    Vin= setup_control[3]
    
    # Define a unique file name for each parameter set3ph_inv_L=1e-4_Ls=1e-4_C=1e-4
    data_file_name = f"./3ph_inv_L={L:.0e}_C={C:.0e}_Lg={Lg:.0e}_V={Vin:.0e}.csv"

    # Start capturing additional signals
    capture.start_capture(duration=0.05, signals=['Ia', 'Ib', 'Ic', 'Inv1.Phase A.PWM_Modulator.TOP_1', 'Inv1.Phase B.PWM_Modulator.TOP_1', 'Inv1.Phase C.PWM_Modulator.TOP_1', 'Inv1.Phase A.PWM_Modulator.BOT_1', 'Inv1.Phase B.PWM_Modulator.BOT_1', 'Inv1.Phase C.PWM_Modulator.BOT_1' ], fileName = data_file_name)

    # Start simulation
    hil.start_simulation()

    df_meas = capture.get_capture_results(wait_capture=True)

    # Stop simulation
    hil.stop_simulation()
    
    return True
