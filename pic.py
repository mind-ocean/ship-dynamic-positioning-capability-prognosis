import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image

import os
import shutil
import pandas as pd
from fpdf import FPDF
from matplotlib import rcParams



def pic(ship_name,thrusters,Lpp, B, x_skeg, y_skeg):
    
    
    # ship
    b=[-B/Lpp/2, B/Lpp/2]
    l=[-0.5,0.5]
    bow=1/3.5
    
    # thrusters
    name=[]
    shapes=[]
    x_thr=[]
    y_thr=[]
    failure=[]
    
    explain=''
    
    for thr in thrusters:
        name.append(thr[0])
        type_thr=thr[1]
        
        choices1={
            'Shaft line FPP without nozzle':'prop',
            'Shaft line FPP with nozzle':'prop',
            'Shaft line CPP without nozzle':'prop',
            'Shaft line CPP with nozzle':'prop',
            'Shaft line CRP':'prop',
            'Azimuth without nozzle':'azi',
            'Azimuth with nozzle':'azi',
            'Azimuth CRP':'azi',
            'pod without nozzle':'pod',
            'pod with nozzle':'pod',
            'pod CRP':'pod',
            'Tunnel thruster':'tunnel',
            'Cycloidal':'azi',   
            }
      
        shape=str(choices1.get(type_thr, 'not in the base'))
        
        shapes.append(shape)
        
        x_thr.append(-float(thr[5])/Lpp)
        y_thr.append(float(thr[4])/Lpp)
        
        P=thr[8]
        
        if P=='0':
            failure.append(1)
        else:
            failure.append(0)
    
    figure,ax=plt.subplots(1,1,figsize=(4,6)) #figize=(7,4)
    figure.tight_layout()
    figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    
    # ship outline
    x=[b[0],b[1],b[1],0,b[0],b[0]]
    y=[l[0],l[0],bow,l[1],bow,l[0]]
    
    #ax.set_box_aspect(1)
    ax.plot(x,y,c='goldenrod',alpha=0.7,zorder=1,linewidth=B/Lpp*25)
    
    ax.text(0,0.5,'    FP')
    ax.text(0+b[1],-0.5,'    AP')
    
    ax.arrow(0, 0, -0.1, 0,head_width=0.015,fc='black',alpha=0.5)
    ax.arrow(0, 0, 0, 0.2,head_width=0.015,fc='black',alpha=0.5)
    ax.text(0.01,0.2,'x')
    ax.text(-0.1,0.01,'y')
    
    # skeg
    for i in range(len(x_skeg)):
        y=x_skeg[i]/Lpp
        x=-y_skeg[i]/Lpp
        
        line=[[x,x],[0-1/5,y]]
        
        ax.plot(line[0],line[1],c='goldenrod',alpha=0.7,zorder=1,linewidth=B/Lpp*25)
        
        
    thr_c='limegreen'
    thr_f='red'
    a=0.7
    
    # thrusters
    for i in range(len(thrusters)):
        x=x_thr[i]
        y=y_thr[i]
        
        #add=str(i+1)+' - '+str(thrusters[i][0])+'\n'
        
        #explain=explain+add
        
        ax.text(x-0.012,y-0.01,str(i+1))
        
        
        if shapes[i]=='tunnel':
            
            w=0.15
            h=0.03
            tunnel = plt.Rectangle((x-w/2,y-h/2), w, h, fc=thr_c if failure[i]==0 else thr_f,alpha=a)
            ax.add_patch(tunnel)
        
        elif shapes[i]=='pod':
            
            rh=0.03
            rv=0.1
            pod =mpl.patches.Ellipse((x,y), rh,rv, fc=thr_c if failure[i]==0 else thr_f,alpha=a)
            ax.add_patch(pod)
        
        elif shapes[i]=='prop':
            
            l=B/Lpp*0.7
            w=0.015
            wp=0.1
            
            rh=0.04
            rv=0.016
            shaft = plt.Rectangle((x-w/2,y), w, l, fc=thr_c if failure[i]==0 else thr_f,alpha=a)
            prop1 = mpl.patches.Ellipse((x-rh/2,y), rh,rv, fc=thr_c if failure[i]==0 else thr_f,alpha=a)
            prop2 = mpl.patches.Ellipse((x+rh/2,y), rh,rv, fc=thr_c if failure[i]==0 else thr_f,alpha=a)
           
            ax.add_patch(shaft)
            ax.add_patch(prop1)
            ax.add_patch(prop2)
        
        else:
            r=0.03
            azi = plt.Circle((x,y), radius=r, fc=thr_c if failure[i]==0 else thr_f,alpha=a)
            ax.add_patch(azi)
            
            
    
    #ax.text(-0.5,0,explain,fontsize=12,color='grey',alpha=0.7)
    
    ax.set_axis_off()
    ax.axis('equal')
    
    plt.savefig('RESULTS/'+str(ship_name)+'/layout.png', dpi=150)

def report(Cap,Angles,ship_name,thrusters,Lpp, B, T, Los, XLos, bow_angle, CWLaft, AF_wind, AL_wind, xL_wind, AL_current, xL_current, gamma, x_skeg, y_skeg, case,points):
   
    image='RESULTS/'+str(ship_name)+'/layout.png'
    im = Image.open(image)
    w,h=im.size
    
    font='Arial'
    pdf = FPDF()
    
    #forbidden zones
    fb_zone=[]
    for i, thr in enumerate(points):
        fb_zone.append([])
        for j,zone in enumerate(thr[0]):
            alfa_start=round(zone[1][0])
            alfa_end=round(zone[3][0])
            
            def_zone=[alfa_start,alfa_end]
            
            fb_zone[i].append(def_zone)
   
    
    # START SHIP DATA I COLUMN -----------------------------------------
    if len(x_skeg)==0:
        skegs=''
        symb=''
        u=''
        val=''
        
    elif len(x_skeg)==1:
        skegs='x position of the skeg aft edge \n' \
            'y position of the skeg aft edge'
        symb='x skeg \n' \
            'y skeg'
        u='m \n'+'m \n'
        val=str(x_skeg[0])+' \n'+str(y_skeg[0])
    else:
        skegs='x position of the skeg 1 aft edge \n' \
            'y position of the skeg 1 aft edge \n' \
               'x position of the skeg 2 aft edge \n' \
                   'y position of the skeg 2 aft edge'
        symb='x skeg 1 \n' \
            'y skeg 1 \n' \
                'x skeg 2 \n' \
                    'y skeg 2'
        u='m \n'+'m \n'+'m \n'+'m'
        
        val=str(x_skeg[0])+' \n'+str(y_skeg[0])+' \n' + str(x_skeg[1])+' \n'+str(y_skeg[1])
    
    list_ship=[Lpp,B,T,Los,XLos, bow_angle, CWLaft, AF_wind, AL_wind, xL_wind, AL_current, xL_current]
    
    data=['Length between perpendiculars',\
          'Maximum breadth at waterline', \
              'Summer load line draft', \
                  'Longitudinal distance between the fore most and aft most point under water', \
                      'Longitudinal position of Los/2', \
                          'Half bow angle of enterance', \
                              'Water plane area coeffcient behind miship', \
                                  'Frontal projected wind area', \
                                      'Longitudinal projected wind area', \
                                          'Longitudinal position of the area center of AL_wind', \
                                              'Longitudinal projected submerged current area', \
                                                  'Longitudinal position of the area center of AL_current']
    
    symb_sh=['Lpp','B','T','Los','XLos','Bow angle','CWL_aft','AF_wind','AL_wind','xL_wind','AL_current','xL_current']
    
    unit='m','m','m','m','m','deg','-','m2','m2','m','m2','m'
    
    header=''
    symbol=''
    units=''
    values=''
    
    for i in range(len(data)):
        
        if (list_ship[i]==0 or list_ship[i]=='0') and case[2]==0 and symb_sh[i]=='XLos':
            
            if i==3 or i==9 or i==10 or i==11:
                a='\n \n'
            else:
                a='\n'
                
            header=header+data[i]+'\n'
            symbol=symbol+symb_sh[i]+a
            units=units+unit[i]+a
            values=values+str(round(list_ship[i],3))+a
            
            
        if list_ship[i]!='0' and list_ship[i]!=0:
            
            if i==3 or i==9 or i==10 or i==11:
                a='\n \n'
            else:
                a='\n'
                
            header=header+data[i]+'\n'
            symbol=symbol+symb_sh[i]+a
            units=units+unit[i]+a
            values=values+str(round(list_ship[i],3))+a
    
    if case[2]==1:
        
        header=header+'gamma \n'
        symbol=symbol+'gamma \n'
        units=units+'- \n'
        values=values+str(gamma)+'\n'
            
        
   
    
    data=header+skegs
    symb=symbol+symb
    unit=units+u
    value=values+val
    
    # END SHIP DATA I COLUMN-------------------------------------------------------------------------------
    
   
    
    
    # STRAT THRUSTERS HEAD------------------------
    
    thr_tab=['Thruster user name','Type','Characteristic','Rudder type','x [m]','y [m]','z [m]','D [m]', \
        'Brake Power [kW]','Type for mech. eff.','Rudder surface [m2]']
    # END THRUSTERS HEAD--------------------------
        
    #-----SHIP TABLE---------------------------------------------
    w1=60
    w2=20
    w3=15
    w4=15
    hs=5
    
        
    hthr=[]
    ctitle=[0,153,153]
    csec=[255,102,102]
    clev=[0,204,204]
    
    
    
    pdf.add_page()
    pdf.set_font(font, 'B', 20)
    pdf.set_text_color(ctitle[0],ctitle[1],ctitle[2]) 
    pdf.cell(w=0, h=15, txt='DP report of : '+str(ship_name), ln=1)
    pdf.set_font(font, 'B', 12)
    pdf.set_text_color(clev[0],clev[1],clev[2]) 
    if case==[0,0,0]:
        pdf.cell(w=0, h=10, txt='DNV Level 1', ln=1)
    
    else:
        
        note=': User defined '
        if case[0]==1:
            note=note+'wind '
        if case[1]==1:
            note=note+'current '
        if case[2]==1:
            note=note+'waves '
        
        note=note+'coefficients'
        pdf.cell(w=0, h=10, txt='DNV Level 2'+note, ln=1)
    
    pdf.set_font(font, 'B', 12)
    pdf.set_text_color(csec[0],csec[1],csec[2])
    pdf.cell(w=0, h=12, txt='Hull data', ln=1)
    
    pdf.set_font(font, '', 10)
    pdf.set_text_color(0,0,0)
    pdf.cell(w=w1,h=hs+2,txt='Data',border='B',ln=0,align='L')
    pdf.cell(w=w2,h=hs+2,txt='Symbol',border='B',ln=0,align='C')
    pdf.cell(w=w3,h=hs+2,txt='Unit',border='B',ln=0,align='C')
    pdf.cell(w=w4,h=hs+2,txt='Value',border='B',ln=1,align='C')
    
    top = pdf.y
    offset = pdf.x + w1
    
    pdf.set_font(font, '', 8)
    pdf.multi_cell( w=w1,h=hs, txt=data, border='B',align='L')
    pdf.y = top
    pdf.x = offset 
    pdf.multi_cell( w=w2,h=hs, txt=symb, border='B',align='C')
    pdf.y = top
    offset = offset+ w2
    pdf.x = offset 
    pdf.multi_cell( w=w3,h=hs, txt=unit, border='B',align='C')
    
    pdf.y = top
    offset = offset+ w3
    pdf.x = offset 
    pdf.multi_cell( w=w4,h=hs, txt=value, border='B',align='C')
 
    width=0.75*(200-(w1+w2+w3+w4))
    height=h/w*width
    xpos=190-width
    pdf.image(image, x=xpos, y=top-8, w=width, h=height, type='PNG')
    
    
    #-------THR TABLE --------------------------------
    pdf.y=160
    pdf.set_font(font, 'B', 12)
    pdf.set_text_color(csec[0],csec[1],csec[2])
    pdf.cell(w=0, h=12, txt='Thrusters data', ln=1)
    
    
    w=30
    w0=20
    
    top = pdf.y
    offset = pdf.x
    
    
    pdf.set_text_color(0,0,0)
    pdf.set_font(font, '', 8)
    
    hs=4
    hthr=[2,4,5,1,1,1,1,1,1,3,1]
    hh=[]
    for i, hi in enumerate(hthr):
        hh.append(hi*hs)
        
    pdf.cell(w=w,h=hs,txt='Thruster No.',border='B',ln=0,align='L')
    
    offset = offset+w
    pdf.set_font(font, 'B', 8)
    for i, thr in enumerate(thrusters):
        pdf.y = top
        pdf.x = offset 
        
        if thr[8]=='0':
            pdf.set_text_color(255,0,0)
        else:
            pdf.set_text_color(0,255,0)
            
            
        pdf.cell(w=w0,h=hs,txt=str(i+1),border='B',ln=0 if i+1<len(thrusters) else 1,align='C')
        
        offset=offset+w0
    
    pdf.set_font(font, '', 8)
    pdf.set_text_color(0,0,0)
    top = pdf.y
    pdf.x=10
    offset=10
    pos=top
    for i, names in enumerate(thr_tab):
        pdf.x=offset
        pdf.y=pos
        pdf.multi_cell(w=w,h=hs,txt=names,border=0 if i+1<len(thr_tab) else 'B',align='L')
        pos=pos+hh[i]
    
    
    for i, thr in enumerate(thrusters):
        offset = 10+w+i*w0
        pdf.y=top
        pos=top
        for j, val in enumerate(thr):
            pdf.x=offset 
            pdf.y=pos
            pdf.multi_cell(w=w0,h=hs,txt=val,border=0 if j+1<len(thr) else 'B',align='C')
            pos=pos+hh[j]
    
    # ----FB ZONE---------------------------------
    pdf.set_text_color(0,0,0)
    pdf.set_font(font, '', 8)
    
    pdf.y=pdf.y+hs
    
    zone_txt='Forbidden zones: '
    for i, zone in enumerate(fb_zone):
        zone_txt=zone_txt+' thr '+str(i+1)+' : '
        if len(zone)!=0:
            for j, z in enumerate(zone):
                zone_txt=zone_txt+str(z[0])+' - '+str(z[1])+' '
        else:
            zone_txt=zone_txt+' None '
        if (i+1)<len(fb_zone):
            zone_txt=zone_txt+' ,'
        
    pdf.multi_cell(w=210,h=hs,txt=zone_txt,border=0,align='L')
    
    
    #----------------------- DP PLOT --------------------------------
    
    pdf.add_page()
    pdf.set_font(font, 'B', 12)
    pdf.set_text_color(csec[0],csec[1],csec[2])
    pdf.cell(w=0, h=12, txt='Results', ln=1)
    
    image='RESULTS/'+str(ship_name)+'/DP_Cap.png'
    im = Image.open(image)
    w,h=im.size
    scale=0.09
    w=w*scale
    h=h*scale
    top=20
    pdf.image(image, x=105-int(w/2), y=top, w=w, h=h, type='PNG')
    
    #---------------------- RES TABLE --------------------------------
    
    waa=25
    wd=25
    w=35
    pdf.y=10+h
    pdf.set_font(font, '', 10)
    pdf.set_text_color(0,0,0)
    pdf.cell(w=waa,h=hs+2,txt='Angle',border='B',ln=0,align='C')
    pdf.cell(w=wd,h=hs+2,txt='DP number',border='B',ln=0,align='C')
    pdf.cell(w=w,h=hs+2,txt='Wind speed [m/s]',border='B',ln=0,align='C')
    pdf.cell(w=w,h=hs+2,txt='Wave height [m]',border='B',ln=0,align='C')
    pdf.cell(w=w,h=hs+2,txt='Peak period [s]',border='B',ln=0,align='C')
    pdf.cell(w=w,h=hs+2,txt='Current speed [m/s]',border='B',ln=1,align='C')
    
    
    wind=np.array([0,1.5,3.4,5.4,7.9,10.7,13.8,17.1,20.7,24.4,28.4,32.6]) 
    wave=np.array([0,0.1,0.4,0.8,1.3,2.1,3.1,4.2,5.7,7.4,9.5,12.1]) 
    period=np.array([0,3.5,4.5,5.5,6.5,7.5,8.5,9,10,10.5,11.5,12]) 
    current=np.array([0,0.25,0.5,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75])
    
    hs=3.1
    pdf.set_font(font, '', 7)
    pdf.set_text_color(0,0,0)
    for i, DP_num in enumerate(Cap):
        
        wi=wind[DP_num]
        wa=wave[DP_num]
        p=period[DP_num]
        c=current[DP_num]
        
        pdf.cell(w=waa,h=hs,txt=str(Angles[i]),border=0,ln=0,align='C')
        pdf.cell(w=wd,h=hs,txt=str(DP_num),border=0,ln=0,align='C')
        pdf.cell(w=w,h=hs,txt=str(wi),border=0,ln=0,align='C')
        pdf.cell(w=w,h=hs,txt=str(wa),border=0,ln=0,align='C')
        pdf.cell(w=w,h=hs,txt=str(p),border=0,ln=0,align='C')
        pdf.cell(w=w,h=hs,txt=str(c),border=0,ln=1,align='C')
    
    wi=wind[Cap[0]]
    wa=wave[Cap[0]]
    p=period[Cap[0]]
    c=current[Cap[0]]
    
    pdf.cell(w=waa,h=hs,txt=str(360),border='B',ln=0,align='C')
    pdf.cell(w=wd,h=hs,txt=str(Cap[0]),border='B',ln=0,align='C')
    pdf.cell(w=w,h=hs,txt=str(wi),border='B',ln=0,align='C')
    pdf.cell(w=w,h=hs,txt=str(wa),border='B',ln=0,align='C')
    pdf.cell(w=w,h=hs,txt=str(p),border='B',ln=0,align='C')
    pdf.cell(w=w,h=hs,txt=str(c),border='B',ln=1,align='C')
    
    
    pdf.output('RESULTS/'+str(ship_name)+'/Report.pdf', 'F')

def report_site(ship_name,thrusters,x_skeg,y_skeg,Lpp, B, T, wind_ang,v_wind, current_ang,v_current, wave_ang, Hs, Tp, Fx_wind, Fy_wind, Mz_wind, Fx_current, Fy_current, Mz_current, Fx_wave, Fy_wave, Mz_wave,points):
    
    image='RESULTS/'+str(ship_name)+'/layout.png'
    im = Image.open(image)
    w,h=im.size
    
    font='Arial'
    pdf = FPDF()
    
    #forbidden zones
    fb_zone=[]
    for i, thr in enumerate(points):
        fb_zone.append([])
        for j,zone in enumerate(thr[0]):
            alfa_start=round(zone[1][0])
            alfa_end=round(zone[3][0])
            
            def_zone=[alfa_start,alfa_end]
            
            fb_zone[i].append(def_zone)
   
    
    # START SHIP DATA I COLUMN -----------------------------------------
    if len(x_skeg)==0:
        skegs=''
        symb=''
        u=''
        val=''
        
    elif len(x_skeg)==1:
        skegs='x position of the skeg aft edge \n' \
            'y position of the skeg aft edge'
        symb='x skeg \n' \
            'y skeg'
        u='m \n'+'m \n'
        val=str(x_skeg[0])+' \n'+str(y_skeg[0])
    else:
        skegs='x position of the skeg 1 aft edge \n' \
            'y position of the skeg 1 aft edge \n' \
               'x position of the skeg 2 aft edge \n' \
                   'y position of the skeg 2 aft edge'
        symb='x skeg 1 \n' \
            'y skeg 1 \n' \
                'x skeg 2 \n' \
                    'y skeg 2'
        u='m \n'+'m \n'+'m \n'+'m'
        
        val=str(x_skeg[0])+' \n'+str(y_skeg[0])+' \n' + str(x_skeg[1])+' \n'+str(y_skeg[1])
    
    list_ship=[Lpp, B, T, wind_ang,v_wind, current_ang,v_current, wave_ang, Hs, Tp]
    
    data=['Length between perpendiculars',\
          'Maximum breadth at waterline', \
              'Summer load line draft', \
                  'Wind angle', \
                      'Wind speed', \
                          'Current angle', \
                              'Current speed', \
                                  'Wave angle', \
                                      'Wave significant height', \
                                          'Wave peak period']
    
    symb_sh=['Lpp','B','T','ang_wi','v_wi','ang_c','v_c','ang_wa','Hs','Tp']
    
    unit='m','m','m','deg','m/s','deg','m/s','deg','m','s'
    
    header=''
    symbol=''
    units=''
    values=''
    
    for i in range(len(data)):        
       
        a='\n'
                
        header=header+data[i]+a
        symbol=symbol+symb_sh[i]+a
        units=units+unit[i]+a
        values=values+str(round(list_ship[i],3))+a
   
    data=header+skegs
    symb=symbol+symb
    unit=units+u
    value=values+val
    
    # END SHIP DATA I COLUMN-------------------------------------------------------------------------------
    
   
    
    
    # STRAT THRUSTERS HEAD------------------------
    
    thr_tab=['Thruster user name','Type','Characteristic','Rudder type','x [m]','y [m]','z [m]','D [m]', \
        'Brake Power [kW]','Type for mech. eff.','Rudder surface [m2]']
    # END THRUSTERS HEAD--------------------------
        
    #-----SHIP TABLE---------------------------------------------
    w1=60
    w2=20
    w3=15
    w4=15
    hs=5
    
        
    hthr=[]
    ctitle=[0,153,153]
    csec=[255,102,102]
    clev=[0,204,204]
    
    
    
    pdf.add_page()
    pdf.set_font(font, 'B', 20)
    pdf.set_text_color(ctitle[0],ctitle[1],ctitle[2]) 
    pdf.cell(w=0, h=15, txt='DP report of : '+str(ship_name), ln=1)
    pdf.set_font(font, 'B', 12)
    pdf.set_text_color(clev[0],clev[1],clev[2]) 
    
    pdf.cell(w=0, h=10, txt='DNV Level 2 - site', ln=1)
    
    pdf.set_font(font, 'B', 12)
    pdf.set_text_color(csec[0],csec[1],csec[2])
    pdf.cell(w=0, h=12, txt='Hull data', ln=1)
    
    pdf.set_font(font, '', 10)
    pdf.set_text_color(0,0,0)
    pdf.cell(w=w1,h=hs+2,txt='Data',border='B',ln=0,align='L')
    pdf.cell(w=w2,h=hs+2,txt='Symbol',border='B',ln=0,align='C')
    pdf.cell(w=w3,h=hs+2,txt='Unit',border='B',ln=0,align='C')
    pdf.cell(w=w4,h=hs+2,txt='Value',border='B',ln=1,align='C')
    
    top = pdf.y
    offset = pdf.x + w1
    
    pdf.set_font(font, '', 8)
    pdf.multi_cell( w=w1,h=hs, txt=data, border='B',align='L')
    pdf.y = top
    pdf.x = offset 
    pdf.multi_cell( w=w2,h=hs, txt=symb, border='B',align='C')
    pdf.y = top
    offset = offset+ w2
    pdf.x = offset 
    pdf.multi_cell( w=w3,h=hs, txt=unit, border='B',align='C')
    
    pdf.y = top
    offset = offset+ w3
    pdf.x = offset 
    pdf.multi_cell( w=w4,h=hs, txt=value, border='B',align='C')
 
    width=0.75*(200-(w1+w2+w3+w4))
    height=h/w*width
    xpos=190-width
    pdf.image(image, x=xpos, y=top-8, w=width, h=height, type='PNG')
    
    
    #-------THR TABLE --------------------------------
    pdf.y=160
    pdf.set_font(font, 'B', 12)
    pdf.set_text_color(csec[0],csec[1],csec[2])
    pdf.cell(w=0, h=12, txt='Thrusters data', ln=1)
    
    
    w=30
    w0=20
    
    top = pdf.y
    offset = pdf.x
    
    
    pdf.set_text_color(0,0,0)
    pdf.set_font(font, '', 8)
    
    hs=4
    hthr=[2,4,5,1,1,1,1,1,1,3,1]
    hh=[]
    for i, hi in enumerate(hthr):
        hh.append(hi*hs)
        
    pdf.cell(w=w,h=hs,txt='Thruster No.',border='B',ln=0,align='L')
    
    offset = offset+w
    pdf.set_font(font, 'B', 8)
    for i, thr in enumerate(thrusters):
        pdf.y = top
        pdf.x = offset 
        
        if thr[8]=='0':
            pdf.set_text_color(255,0,0)
        else:
            pdf.set_text_color(0,255,0)
            
            
        pdf.cell(w=w0,h=hs,txt=str(i+1),border='B',ln=0 if i+1<len(thrusters) else 1,align='C')
        
        offset=offset+w0
    
    pdf.set_font(font, '', 8)
    pdf.set_text_color(0,0,0)
    top = pdf.y
    pdf.x=10
    offset=10
    pos=top
    for i, names in enumerate(thr_tab):
        pdf.x=offset
        pdf.y=pos
        pdf.multi_cell(w=w,h=hs,txt=names,border=0 if i+1<len(thr_tab) else 'B',align='L')
        pos=pos+hh[i]
    
    
    for i, thr in enumerate(thrusters):
        offset = 10+w+i*w0
        pdf.y=top
        pos=top
        for j, val in enumerate(thr):
            pdf.x=offset 
            pdf.y=pos
            pdf.multi_cell(w=w0,h=hs,txt=val,border=0 if j+1<len(thr) else 'B',align='C')
            pos=pos+hh[j]
    
    # ----FB ZONE---------------------------------
    pdf.set_text_color(0,0,0)
    pdf.set_font(font, '', 8)
    
    pdf.y=pdf.y+hs
    
    zone_txt='Forbidden zones: '
    for i, zone in enumerate(fb_zone):
        zone_txt=zone_txt+' thr '+str(i+1)+' : '
        if len(zone)!=0:
            for j, z in enumerate(zone):
                zone_txt=zone_txt+str(z[0])+' - '+str(z[1])+' '
        else:
            zone_txt=zone_txt+' None '
        if (i+1)<len(fb_zone):
            zone_txt=zone_txt+' ,'
        
    pdf.multi_cell(w=210,h=hs,txt=zone_txt,border=0,align='L')
    
       
    pdf.output('RESULTS/'+str(ship_name)+'/Report.pdf', 'F')