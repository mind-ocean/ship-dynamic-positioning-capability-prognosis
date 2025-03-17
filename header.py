

def header(num_thr,name_thr):
    
    
    for num_n in range(len(name_thr)):
        name_thr[num_n]=name_thr[num_n].replace(' ','_')
  
    head=['Angle','DP_number']
    
    for num in range(num_thr):
        
        head.append('Thrust_angle_[deg]_thr_'+str(num+1)+'_:_'+str(name_thr[num]))    
        head.append('Rudder_angle_[deg]_thr'+str(num+1)+'_:_'+str(name_thr[num]))
        head.append('Nominal_thrust_utilisation_[%]_thr'+str(num+1)+'_:_'+str(name_thr[num]))
        head.append('Effective_thrust_[kN]_thr'+str(num+1)+'_:_'+str(name_thr[num]))
        head.append('Tx_rudder_[kN]_thr'+str(num+1)+'_:_'+str(name_thr[num]))
        head.append('Ty_rudder_[kN]_thr'+str(num+1)+'_:_'+str(name_thr[num]))
        head.append('Thrust_loss_factor_thr'+str(num+1)+'_:_'+str(name_thr[num]))
        head.append('Utilized_power_[kW]_thr'+str(num+1)+'_:_'+str(name_thr[num]))
       
    
    head.append('Fx_current_[kN]')
    head.append('Fy_current_[kN]')
    head.append('Mz_currentk_[N]')
    head.append('Fx_wave_[kN]')
    head.append('Fy_wave_[kN]')
    head.append('Mz_wave_[kN]')
    head.append('Fx_wind_[kN]')
    head.append('Fy_wind_[kN]')
    head.append('Mz_wind_[kN]')

    
    for num in range(num_thr):
        name1='solution_Tx_[kN]_thr'+'_:_'+str(name_thr[num])
        head.append(name1)
        
        name1='solution_Ty_[kN]_thr'+'_:_'+str(name_thr[num])
        head.append(name1)
    
    return head


