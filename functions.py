import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d


def import_file_txt(file_name):
    
    path=file_name
    df=pd.read_csv(path,sep=' ')
    
    return df

def import_file_data(file_name):
    
    path=file_name
    df=pd.read_csv(path,sep=',')
    
    return df

class ship_data_preparation:
    def __init__(self,ship_data):
        self.ship_data = ship_data
        
    def to_thr(self):
        
        ship_data = self.ship_data
        ship_name = ship_data[0]
        num_thr = int(ship_data[1])
        num_skeg = int(ship_data[2])
        
        thr_len = 11 * num_thr
        all_data_len = len(ship_data)
        index_skeg = all_data_len - thr_len - 1
        
        x = 1
        y = 0
        x_skeg = []
        y_skeg = []
        
        for i in range(num_skeg):
            x_skeg.append(float(ship_data[index_skeg - x]))
            x=x - 2
            y_skeg.append(float(ship_data[index_skeg - y]))
        
        
        thrusters = []
        first_thr = index_skeg + 1
        
        for i in range(num_thr):
            
            thrusters.append([])
            last_index = first_thr + 11
            list_thr = ship_data[first_thr:last_index]
            first_thr = first_thr + 11
            
            thrusters[i] = list_thr
            
        
        return x_skeg, y_skeg, thrusters, num_thr, ship_name
            
def convert(seconds):
    minutes, sec = divmod(seconds, 60)
    hour, minutes = divmod(minutes, 60)
    
    return '%d:%02d:%02d' % (hour, minutes, sec)
