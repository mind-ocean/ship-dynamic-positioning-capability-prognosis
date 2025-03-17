

import numpy as np
import streamlit as st
from main import*
from PIL import Image
import shutil
import pandas as pd
from io import StringIO

df = pd.read_csv('wind.csv',sep=';')
in_df=df.values.tolist()


import csv

with open("wind.csv", "w", newline="") as f:
    writer = csv.writer(f,delimiter=';')
    writer.writerow(['angle','cx','cy','cn'])
    writer.writerows(in_df)
    
                with open("RESULTS/wind.csv", "w", newline="") as f:
                    writer = csv.writer(f,delimiter=';')
                    writer.writerow(['angle','cx','cy','cn'])
                    writer.writerows(wind_data)
       
            if current_load is not None:
                df_current= pd.read_csv(current_load,sep=';')
                current_data=df_current.values.tolist()
                
                with open("RESULTS/current.csv", "w", newline="") as f:
                    writer = csv.writer(f,delimiter=';')
                    writer.writerow(['angle','cx','cy','cn'])
                    writer.writerows(current_data)
                
            
            if wind_load is not None:
                df_wave = pd.read_csv(wave_load,sep=';')
                wave_data=df_wave.values.tolist()
                
                with open("RESULTS/wave.csv", "w", newline="") as f:
                    writer = csv.writer(f,delimiter=';')
                    writer.writerow(['angle','cx','cy','cn'])
                    writer.writerows(wave_data)
              