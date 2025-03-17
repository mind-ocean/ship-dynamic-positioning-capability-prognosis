"""
Environmental forces calculation for one iteration
"""

#import of liblaries
import math
import numpy as np
import matplotlib.pyplot as plt


class environment:
    def __init__(self,angle,DP_num,Lpp,B,T,Los,Xlos,bow_angle,CWLaft,AF_wind,AL_wind,xL_wind,AL_current,xL_current,gamma,ro_water,case,wind_data,current_data,wave_data_x,wave_data_y,wave_data_z):
        self.angle=angle
        self.DP_num=DP_num
        self.Lpp=Lpp
        self.B=B
        self.T=T
        self.Los=Los   
        self.Xlos=Xlos
        self.bow_angle=bow_angle
        self.CWLaft=CWLaft
        self.AF_wind=AF_wind
        self.AL_wind=AL_wind
        self.xL_wind=xL_wind
        self.AL_current=AL_current
        self.xL_current=xL_current
        self.gamma=gamma
        self.ro_water=ro_water
        self.case=case
        self.wind_data=wind_data
        self.current_data=current_data
        self.wave_data_x=wave_data_x
        self.wave_data_y=wave_data_y
        self.wave_data_z=wave_data_z
 
    
    def condition(self):
        """ here you will find the whole DNV GL environment table"""
        DP_num=self.DP_num
        
        #Weather condition arrays        
        #wind speed in m/s
        wind=np.array([0,1.5,3.4,5.4,7.9,10.7,13.8,17.1,20.7,24.4,28.4,32.6])        
        #wave height in m
        wave=np.array([0,0.1,0.4,0.8,1.3,2.1,3.1,4.2,5.7,7.4,9.5,12.1])        
        #peak wave perion in s
        period=np.array([0,3.5,4.5,5.5,6.5,7.5,8.5,9,10,10.5,11.5,12])        
        #current speed in m/s
        current=np.array([0,0.25,0.5,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75])
        
        wi=wind[DP_num]
        wa=wave[DP_num]
        p=period[DP_num]
        c=current[DP_num]
            
        return (wi, wa, p, c)
    
    def forwaves(self):
        angle=self.angle
        Lpp=self.Lpp    
        B=self.B
        bow_angle=self.bow_angle
        CWLaft=self.CWLaft
        
        wi, wa, p, c =self.condition()
         
        #Changing to radians for further calculations
        angle_rad=math.radians(angle)
        
        #Conversion of bow angle to radians
        bow_angle=math.radians(bow_angle)
        
        if CWLaft<0.85:
            CWLaft=0.85
        elif CWLaft>=1.15:
            CWLaft=1.15
        
        h1a=0.8*bow_angle**0.45
        h1b=0.7*CWLaft**2
        
        if angle_rad>=0 and angle_rad<=math.pi:
            direct=angle_rad
        else:
            direct=2*math.pi-angle_rad
            
        #Auxiulary variables
        h1=h1a+(direct/math.pi)*(h1b-h1a)
        h2=0.05+0.95*math.atan(1.45*(direct-1.75))
        h=0.09*h1*h2
        
        #Calculation for waves estimation purposes
        T_prim_surge=p/1.4049/(0.9*Lpp**0.33)
            
        if T_prim_surge<1:
            T_prim_surge=1
        else:
            T_prim_surge=(T_prim_surge**(-3)*math.exp( 1-T_prim_surge**(-3)))
            
            
        T_prim_sway=p/1.4049/(0.75*B**0.5)
        
        if T_prim_sway<1:
            T_prim_sway=1
        else:
            T_prim_sway=(T_prim_sway**(-3)*math.exp(1-T_prim_sway**(-3)))
        
        return (h, direct, T_prim_surge, T_prim_sway)
    
    def wind_coeff(self,Lpp,AF_wind,AL_wind,wi,wind_data,k):
        angle=self.angle
        ro_air=1.23
        
        ang=[]
        cx_=[]
        cy_=[]
        cn_=[]
        
        for i,item in enumerate(wind_data):
            ang.append(item[0])
            cx_.append(item[1])
            cy_.append(item[2])
            cn_.append(item[3])
            
        ind=ang.index(angle)
        
        cx=cx_[ind]
        cy=cy_[ind]
        cn=cn_[ind]
        
        
        #----------WIND---------------------------
        
        Fx_wind=0.5*ro_air*wi**2*AF_wind*cx*k
        Fy_wind=0.5*ro_air*wi**2*AL_wind*cy*k
        Mz_wind=0.5*ro_air*wi**2*Lpp*AL_wind*cn*k
        
        return Fx_wind, Fy_wind,Mz_wind
            
        
    def current_coeff(self,Lpp,B,T,c,current_data,k):
        angle=self.angle
        ro_water=self.ro_water
        
        ang=[]
        cx_=[]
        cy_=[]
        cn_=[]
        
        for i,item in enumerate(current_data):
            ang.append(item[0])
            cx_.append(item[1])
            cy_.append(item[2])
            cn_.append(item[3])
            
        ind=ang.index(angle)
        
        cx=cx_[ind]
        cy=cy_[ind]
        cn=cn_[ind]
        
       
        
        #----------CURRENT-----------------------
        
        Fx_current=0.5*ro_water*c**2*B*T*cx*k
        Fy_current=0.5*ro_water*c**2*T*Lpp*cy*k
        Mz_current=0.5*ro_water*c**2*T*Lpp**2*cn*k
        
        return Fx_current, Fy_current,Mz_current
    
    def spectra(self,omega,Hs,Tp,gamma):
        
        omegap=2*np.pi/Tp
        Agamma=1-0.287*np.log(gamma)
        
        if omega<=omegap:
            sigma=0.07
        else:
            sigma=0.09
            
        Spm=5/16*Hs**2*omegap**4*omega**(-5)*np.exp(-5/4*(omega/omegap)**(-4))
        
        
        n=np.exp(-0.5*((omega-omegap)/(sigma*omegap))**2)
        S=Agamma*Spm*gamma**n
        
        return S
        
    def drift_force(self,x,y,angle,Hs,Tp,gamma):
        
        F=0
        
        for i in range(len(x)-1):
            F=F+(self.spectra(x[i],Hs,Tp,gamma)*y[i]*(x[i+1]-x[i]))
        
        F=F+(self.spectra(x[len(x)-1],Hs,Tp,gamma)*y[len(x)-1]*(x[len(x)-1]-x[len(x)-2]))
            
        F=2*F
        
        return F
    
    def wave_fun(self,data,angle,Hs,Tp,gamma):
        
        angles=list(np.linspace(0,360,37))
        omega=data[0]
        
        ind=angles.index(angle)
        
        ind=ind+1
        
        F=self.drift_force(omega,data[ind],angle,Hs,Tp,gamma)
        
        return F
    
    def wave_coeff(self,gamma,wa,wave_data_x,wave_data_y,wave_data_z,k):
        angle=self.angle
        ro_water=self.ro_water
        g=9.81
        
        wi, wa, Tp, c =self.condition()
        
        x=np.transpose(wave_data_x)
        y=np.transpose(wave_data_y)
        m=np.transpose(wave_data_z)
        
        
        Fx_wave=self.wave_fun(x,angle,wa,Tp,gamma)*k
        Fy_wave=self.wave_fun(y,angle,wa,Tp,gamma)*k
        Mz_wave=self.wave_fun(m,angle,wa,Tp,gamma)*k
       
        
        return Fx_wave, Fy_wave,Mz_wave
    
    def forces(self):
        angle=self.angle
        Lpp=self.Lpp   
        B=self.B
        T=self.T
        Los=self.Los
        Xlos=self.Xlos
        AF_wind=self.AF_wind
        AL_wind=self.AL_wind
        xL_wind=self.xL_wind
        AL_current=self.AL_current
        xL_current=self.xL_current
        gamma=self.gamma
        ro_water=self.ro_water
        case=self.case
        wind_data=self.wind_data
        current_data=self.current_data
        wave_data_y=self.wave_data_y
        wave_data_z=self.wave_data_z
        wave_data_x=self.wave_data_x
        
        wi, wa, p, c =self.condition()
        h, direct, T_prim_surge, T_prim_sway = self.forwaves()
        
        #Constants
        ro_air=1.23
        g=9.81
        k=1.25 #dynamic factor
        
        #Changing to radians for further calculations
        angle_rad=math.radians(angle)
        
        #Forces calculation
        
        if case[0]==0:
        #----------WIND---------------------------
        
            Fx_wind=0.5*ro_air*wi**2*AF_wind*(-0.7*math.cos(angle_rad))*k
            Fy_wind=0.5*ro_air*wi**2*AL_wind*(0.9*math.sin(angle_rad))*k
            Mz_wind=Fy_wind*(xL_wind+0.3*(1-2*(direct/math.pi))*Lpp)
        
        else:
            Fx_wind,Fy_wind,Mz_wind=self.wind_coeff(Lpp,AF_wind,AL_wind,wi,wind_data,k)
            
        if case[1]==0:   
        #----------CURRENT-----------------------
        
            Fx_current=0.5*ro_water*c**2*B*T*(-0.07*math.cos(angle_rad))*k
            Fy_current=0.5*ro_water*c**2*AL_current*(0.6*math.sin(angle_rad))*k
            Mz_current=Fy_current*(xL_current+max(min(0.4*(1-2*(direct/math.pi)),0.25),-0.2)*Lpp)
        
        else:
            Fx_current, Fy_current,Mz_current=self.current_coeff(Lpp,B,T,c,current_data,k)
        
            
        if case[2]==0:    
        #----------WAVES-------------------------
                
            Fx_wave=0.5*ro_water*g*wa**2*B*h*T_prim_surge*k
            Fy_wave=0.5*ro_water*g*wa**2*Los*(0.09*math.sin(angle_rad)*T_prim_sway)*k
            Mz_wave=Fy_wave*(Xlos+(0.05-0.14*(direct/math.pi))*Los)
            
            
        
        else:
            Fx_wave, Fy_wave,Mz_wave= self.wave_coeff(gamma,wa,wave_data_x,wave_data_y,wave_data_z,k)
        
        #if angle==180:
            #print(wa,Fx_wave/k,Fy_wave/k,Mz_wave/k)
        
        #if angle==180:
            #print(wi,Fx_wind,Fy_wind,Mz_wind)
        
        Fx=Fx_wind+Fx_current+Fx_wave
        Fy=Fy_wind+Fy_current+Fy_wave
        Mz=Mz_wind+Mz_current+Mz_wave
        
        env_all=[Fx_current/k,Fy_current/k,Mz_current/k,Fx_wave/k,Fy_wave/k,Mz_wave/k,Fx_wind/k,Fy_wind/k,Mz_wind/k]
        
        b=[-Fx, -Fy, -Mz] # zero is for tunnel thruster
        
        b=np.array(b)
        
        return b, env_all # vector of forces and moment  
    
