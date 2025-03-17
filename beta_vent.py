"""
Ventilation losses calculation for one iteration
"""

#import of liblaries

import numpy as np
from statistics import NormalDist
from thrust_power import*

class ventilation:
    def __init__(self,angle,wa,p,thr_data,Lpp,T,num_thr,vent_factor):
        self.angle=angle
        self.wa=wa
        self.p=p
        self.thr_data=thr_data  
        self.Lpp=Lpp
        self.T=T
        self.num_thr=num_thr
        self.vent_factor=vent_factor
    
                
    def beta_ventilation(self,Tnom,vent_check,beta_loss):
        # calc for each thr - output is a list
        
        num_thr=self.num_thr
        thr_data=self.thr_data
        
        
        beta_vent_loss=[]
        for i in range(num_thr):
            if thr_data[i][7]!=0:
                beta_v=self.beta_vent_i(i,Tnom,vent_check,beta_loss)
                beta_vent_loss.append(beta_v)
            
            else:
                beta_vent_loss.append(0)
        
        return beta_vent_loss
  
    def calc_A(self,i): 
        # calculates A for beta vent
        
        Lpp=self.Lpp
        angle=self.angle
        thr_data=self.thr_data
        p=self.p
        
        
        pi=np.pi
        
        # setting the B
        kv5=0.38
        
        if angle<=180:
            direction=np.radians(angle)
        else:
            direction=np.radians(angle)-2*pi
            
        if direction>=-pi/2 and direction<=pi/2:
            B=1+kv5*np.abs(direction)/pi
        else:
            B=(1+kv5)-kv5*np.abs(direction)/pi
            
        # setting the C
        if thr_data[i][3]>=0:
            C=1
        else:
            C=1+0.4*thr_data[i][3]/Lpp
            
        
        kv4=0.85   
        A1=kv4*B*C  
        
        # OLD LOSS
        if direction>=-pi/2 and direction<=pi/2:
            B=1+np.abs(direction)/pi
        else:
            B=2-np.abs(direction)/pi
        
        # setting the C
        if thr_data[i][3]>=0:
            C=1
        else:
            C=1+0.4*thr_data[i][3]/Lpp
        
        A2=B*C
            
            
        return A1, A2
        
    def beta_vent_i(self,i,Tnom,vent_check,beta_loss):
        # calc beta_vent for i-th thruster
        
        wa=self.wa
        p=self.p
        thr_data=self.thr_data
        T=self.T
        Lpp=self.Lpp
        num_thr=self.num_thr
        vent_factor=self.vent_factor
        
        D=thr_data[i][6]
       
        
        kv1=2
        kv2=1.5
        kv3=15.2
        draft=T-thr_data[i][5]
        
        
        Tz=p/1.4049
        
        if p==0:
            T0=Tz
        else:
            T0=(0.64*Lpp**0.5)/Tz
        
        A1,A2=self.calc_A(i)
        
        """
        if vent_check==0:
            sigma=0.25*wa*A2*min(T0,1)        
            beta_v=(draft-0.75*D)/sigma        
            beta_v=NormalDist(mu=0, sigma=1).cdf(beta_v)
        
        else:
            
            pl=np.abs(Tnom[i])/D**3 # propeller load
            plf=pl**0.5/kv3  # propeller load factor
            sigma_vent=0.25*(wa*A1*min(T0,1)+max((plf-1),0))
            beta_v=kv1*(2*draft/D)-kv2*sigma_vent
            beta_v=NormalDist(mu=0, sigma=1).cdf(beta_v)
           
            T_nom=Tnom[i]*(beta_loss[i]/beta_v)
            
        """
        
        thrust_pow=thrust_power(thr_data,1, 1,num_thr)
        T_nom=thrust_pow.T_max(i)
        
        pl=np.abs(T_nom)/D**3 # propeller load
        plf=pl**0.5/kv3  # propeller load factor
        sigma_vent=0.25*(wa*A1*min(T0,1)+max((plf-1),0))            
        beta_v=kv1*(2*draft/D)-kv2*sigma_vent            
        beta_v=NormalDist(mu=0, sigma=1).cdf(beta_v)
        beta_v=min(beta_v*vent_factor,1)
        
        if p == 0:
            beta_v = 1
            
        return beta_v
