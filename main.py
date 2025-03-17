"""
This script gathers all linked subprograms

In this ver2 we apply updated ventilation losses, mechanical efficiencies
all according to DNV ST0111 2021
"""
from thruster_loop import*
import time
from header import*
from rudders import*
from rudders_new import*
from plot import*
from result import*
from balance import*
from Inequality_constraints_new import*
from thrust_power import*
from beta_vent import*
from env import*
from thr_interactions import*
from pic import*
import numpy as np
import matplotlib.pyplot as plt
from qpsolvers import solve_qp
import pandas as pd
import os
import csv
import streamlit as st
import warnings
warnings.filterwarnings("ignore")


# ------------------------------------------------------------

Lpp = 86.56
B = 18.8
T = 5

Los = 95.85
XLos = -0.13

bow_angle = 27.4
CWLaft = 1.034

x_skeg = [-37.8]
y_skeg = [0]

AF_wind = 391.7
AL_wind = 1203.3
xL_wind = 6.014
AL_current = 440.9
xL_current = 4.717



thrusters=[['thr1','Azimuth without nozzle','Only forward mode *except tunnel thruster','No rudder', \
            '-41.076','4.69','1.54','3.1','1325','tunnel or azimuth','0'], \
           ['thr2','Azimuth without nozzle','Only forward mode *except tunnel thruster','No rudder', \
            '-41.076','-4.69','1.54','3.1','1325','tunnel or azimuth','0'], \
               ['thr3','Azimuth with nozzle','Only forward mode *except tunnel thruster','No rudder', \
            '34.12','0','-1.1','1.65','880','tunnel or azimuth','0'], \
            ['thr4','Tunnel thruster','If tunnel thruster  - option 1 - broken inlet','No rudder', \
            '37.12','0','2','1.74','900','tunnel or azimuth','0'], \
            ['thr5','Tunnel thruster','If tunnel thruster  - option 1 - broken inlet','No rudder', \
            '40.72','0','2','1.74','900','tunnel or azimuth','0']]


ship_name = 'Ratownik'


# ------------------------------------------------------------

num_thr = len(thrusters)


class main:
    def __init__(self, num_thr, ship_name):
        self.num_thr = num_thr
        self.ship_name = ship_name

    def solver(self, thrusters, Lpp, B, T, Los, XLos, bow_angle, CWLaft, AF_wind, AL_wind, xL_wind, AL_current, xL_current, gamma, x_skeg, y_skeg, case, wind_data, current_data, wave_data_x, wave_data_y, wave_data_z):
        
        class_thr = prepare_matrix_thr(thrusters)
        thr_data, name_thr = class_thr.thr_data_m()

        ship_name = self.ship_name
        num_thr = self.num_thr

        if os.path.exists('RESULTS/'+str(ship_name)):
            a = 1

        else:
            os.mkdir('RESULTS/'+str(ship_name))
        
       
        start = time.time()
        name = ship_name
        e = 0.99
        rudder_angle_step = 5
        rudder_max_angle = 30
        ro_water = 1026
        vent_factor = 1

        # Get the thr data
        # thr=thruster_looping(num_thr)
        # thr_data=thr.thruster_matrix()

        # propeller rudder
        prop = propeller_rudder(
            thr_data, num_thr, rudder_angle_step, rudder_max_angle)
        ax, ay, at = prop.coeff()
        
        # Thrusters/skeg interactions
        interactions = thr_int(thr_data, num_thr, y_skeg, x_skeg)
        thr_thr = interactions.work_thr_thr()
        thr_dead = interactions.dead_thr_thr()
        thr_skeg = interactions.skeg_int()
        
        # Interactions function - points
        function = thr_int_points(
            thr_thr, thr_dead, thr_skeg, thr_data, num_thr, x_skeg, y_skeg)
        points = function.joined_points()
        specific_int, int_gather_all_thr = function.exist_fun()

        multi_loss = multiloss(points)
        points = multi_loss.newnew()

        # resulting points for each thruster
        function_modify = new_points(points, num_thr, int_gather_all_thr)
        thr_int_def = function_modify.all_thr_int_points()

        head = header(num_thr,name_thr)

        # start of the loop
        Cap = []
        Angles = []
        Results_DNV = []
        Results_DNV.append(head)
        Results_DNV_max = []
        Results_DNV_max.append(head)
        count = 1
        for i in range(36):  # 36
            angle = i*10 # i*10
            Angles.append(angle)  # recording the current angle
            solver = 1
            j = 0
            #print('Angle: '+str(angle))
            while solver > 0: #  for j in range(1): #

                count = count+1
                j = j+1  # j+1
                DP_num = j  # j
                Results_line = []

                #print('DP: '+str(DP_num))

                # calc forces and get the environment data
                forces = environment(angle, DP_num, Lpp, B, T, Los, XLos, bow_angle, CWLaft,
                                     AF_wind, AL_wind, xL_wind, AL_current, xL_current, gamma, ro_water, case, wind_data, current_data, wave_data_x, wave_data_y, wave_data_z)  # class call
                b_, env_all = forces.forces()
                wi, wa, p, c = forces.condition()

                vent_check = 0
                Tnom = []
                beta_loss = []
                vent = ventilation(angle, wa, p, thr_data,
                                   Lpp, T, num_thr, vent_factor)
                beta_vent_loss = vent.beta_ventilation(
                    Tnom, vent_check, beta_loss)
                beta_loss = beta_vent_loss

                # if angle==20:
                # print(beta_vent_loss[2])

                # the rest of the losses
                beta_misc = 0.9

                # maximum thrust - nominal and effective
                thrust = thrust_power(
                    thr_data, beta_vent_loss, beta_misc, num_thr)
                T_nom, T_eff = thrust.thrust_val()
                
                # print(T_eff)
                # weight for P matrix and radius of thr - ONLY WORKING THRUSTERS WITH NO ZERO LOSSES
                weight, radius = thrust.weight(e)

                # Power coefficients
                P, q = thrust.P_matrix(weight)

                # constraints for the propellers
                rud_simple=rudders_new(rudder_max_angle,T_eff,thr_data,rudder_angle_step)
                G_prop, h_prop=rud_simple.con_prop()
                
                
                #prop_con = propellers(ax, ay, at, num_thr, thr_data, T_eff)
                #G_prop, h_prop = prop_con.con_all()
                
                # Inequality constraints
                ineq = groups(thr_int_def, thr_data, T_eff, num_thr, e, at)
                G, h, loss = ineq.G_h_all()
                
                
                # joining the constraints for the porpellers and other thrusters
                join = concatenate_Gh(G_prop, h_prop, G, h, T_eff, thr_data)
                G_new, h_new, op, pp = join.combain()
                
                
                #comb_thr_prop = prop_con.combo_ax_ay(op, pp)
                #print(comb_thr_prop)
                # Combinantions of all possible alternatives of G and h, loss and ax,ay
                combinations = clear_and_comb(G_new, h_new, loss)
                G_comb = combinations.sym_all()
                h_comb = combinations.h_prep()
                loss_comb = combinations.loss_prep()
                
                tunnel = tunnel_thr(thr_data, num_thr, G_comb, h_comb, T_eff)
                G_new, h_new, div = tunnel.new_G_new_h()
                
                
                # Equality constraints
                bal = balance(thr_data, num_thr, T_eff, b_)
                A = bal.balance_matrix()
                
                b = bal.b_array()
                all_lines = bal.add_lines(at)
                A = bal.combination_A(A, all_lines, op, pp)
                
                
                
                options = len(G_new)  # G_new
                #print(options)
                power = []
                sol = []
                k_res = []
                l = -1
                
                for k in range(options):  # for k in range(options):

                    if div != 0:
                        if k % div == 0:
                            l = l+1
                    else:
                        l = k

                    G_k = G_new[k]
                    h_k = h_new[k]
                    A_k = A[l]
                    loss_k = loss_comb[l]
                    
                    #if k==0:
                        #print(G_k)
                        #print(h_k)
                        
                        #print('----------------------')
                            
                    P_k = thrust.correct_P(P, loss_k, weight, l)

                    try:
                        # CORE FUNCTION
                        solution = solve_qp(
                            P_k, q, G_k, h_k, A_k, b, solver='quadprog')  # CORE FUNCTION

                        solver = 1

                    except:
                        solver = 0
                        solution = None

                    if solution is None or solver == 0:
                        solver = 0
                        k_res.append(0)

                    else:
                        solver = 1
                        k_res.append(1)

                    if solver == 1:
                        
                        res = results(solution, weight, thr_int_def, T_eff, thr_data, num_thr, beta_vent_loss, beta_misc,
                                      ax, ay, at, rudder_max_angle, rudder_angle_step, pp)
                        Pb_total, Pb_list, P_max_list, uti_power = res.total_power()

                        sol.append(solution)
                        power.append(Pb_total)
                
                
                if sum(k_res) != 0 and vent_check == 0:
                    solver = 1
                    min_power = min(power)
                    k_best = power.index(min_power)
                    solution = sol[k_best]
                    res = results(solution, weight, thr_int_def, T_eff, thr_data, num_thr,
                                  beta_vent_loss, beta_misc, ax, ay, at, rudder_max_angle, rudder_angle_step, pp)
                    Tnom, Teff, Tnom_per_max, Teff_per_Tnom, beta_new, rudrud = res.postproc()

                if sum(k_res) != 0:

                    solver = 1
                    min_power = min(power)
                    k_best = power.index(min_power)
                    solution = sol[k_best]
                    res = results(solution, weight, thr_int_def, T_eff, thr_data, num_thr,
                                  beta_vent_loss, beta_misc, ax, ay, at, rudder_max_angle, rudder_angle_step, pp)
                    Pb_total, Pb_list, P_max_list, uti_power = res.total_power()
                    Tnom, Teff, Tnom_per_max, Teff_per_Tnom, beta_new, rudrud = res.postproc()
                    loss_total = res.all_losses()
                    Tx_rud, Ty_rud, angle_rud = res.prop_rudder()

                    Results_line.append(angle)
                    Results_line.append(DP_num)
                    
                    for n in range(num_thr):
                        
                        Results_line.append(beta_new[n])
                        Results_line.append(rudrud[n])
                        Results_line.append(Tnom_per_max[n])
                        Results_line.append(Teff[n])
                        Results_line.append(Tx_rud[n])
                        Results_line.append(Ty_rud[n])
                        Results_line.append(loss_total[n])
                        Results_line.append(Pb_list[n])

                    for n in range(len(env_all)):  # <--------
                        Results_line.append(round(env_all[n]/1000,1))
                    
                    n=0
                    for sss in range(num_thr):
                        
                        if thr_data[sss][7]==0:
                            Results_line.append('N/A')
                            Results_line.append('N/A')
                            
                        else:
                            Results_line.append(round(solution[n]/1000,1))
                            n=n+1
                            Results_line.append(round(solution[n]/1000,1))
                            n=n+1
                        
                        

                    Results_DNV.append(Results_line)

                else:

                    solver = 0
                    Cap.append(DP_num-1)
                    count = int(count-2)
                    if (DP_num-1) > 0:
                        line_max = Results_DNV[count]
                        Results_DNV_max.append(line_max)
                        count = count+1

                if DP_num == 11 and solver == 1:
                    solver = 0
                    Cap.append(DP_num)
                    count = int(count-1)  # -1

                    line_max = Results_DNV[count]
                    Results_DNV_max.append(line_max)
                    count = count+1

        res_out = Results_DNV_max
        
        res_file = open("RESULTS/"+str(ship_name)+"/res.txt", "w")
        np.savetxt(res_file, res_out, '%s')
        res_file.close()

        res_all = Results_DNV

        res_file_all = open("RESULTS/"+str(ship_name)+"/res_all.txt", "w")
        np.savetxt(res_file_all, res_all, '%s')
        res_file_all.close()

        with open('RESULTS/'+str(ship_name)+'/res.txt', 'r') as my_file:
            text = my_file.read()
            text = text.replace("[", "")
            text = text.replace("'", "")
            text = text.replace("]", "")
            text = text.replace(",", "")

        with open('RESULTS/'+str(ship_name)+'/res.txt', 'w') as w:
            w.write(str(text))

        with open('RESULTS/'+str(ship_name)+'/res_all.txt', 'r') as my_file:
            text = my_file.read()
            text = text.replace("[", "")
            text = text.replace("'", "")
            text = text.replace("]", "")
            text = text.replace(",", "")

        with open('RESULTS/'+str(ship_name)+'/res_all.txt', 'w') as w:
            w.write(str(text))
        
        
        # INPUT ***********
        num_skeg = len(x_skeg)
        input_data = [ship_name, num_thr, num_skeg, Lpp, B, T, Los, XLos, bow_angle,
                      CWLaft, AF_wind, AL_wind, xL_wind, AL_current, xL_current, gamma]

        if len(x_skeg) == 1 and x_skeg[0] != 0:
            input_data.append(x_skeg[0])
            input_data.append(y_skeg[0])

        elif len(x_skeg) == 2:
            input_data.append(x_skeg[0])
            input_data.append(y_skeg[0])
            input_data.append(x_skeg[1])
            input_data.append(y_skeg[1])

        for i, item in enumerate(input_data):
            item = str(item)

        for z in range(num_thr):
            for x in range(len(thrusters[z])):
                input_data.append(thrusters[z][x])

        name_ = 'RESULTS/'+str(ship_name)+'/input.csv'
        df = pd.DataFrame(input_data)
        df.to_csv(name_)

       
       
        Cap = np.array(Cap)
        Angles = np.array(Angles)
        
        

        end = time.time()
        duration = end-start
        post = postprocessing(Cap, Angles, ship_name)
        plot = post.polarplot()
        
        
        pic(ship_name,thrusters,Lpp, B, x_skeg, y_skeg)
        report(Cap,Angles,ship_name,thrusters,Lpp, B, T, Los, XLos, bow_angle, CWLaft, AF_wind, AL_wind, xL_wind, AL_current, xL_current, gamma, x_skeg, y_skeg, case, points)
        
        
        return duration, 'Yaaayy! :)'

duration, message = main(num_thr, ship_name).solver(thrusters, Lpp, B, T, Los, XLos, bow_angle, CWLaft, AF_wind, AL_wind,xL_wind, AL_current, xL_current, 0, x_skeg, y_skeg, [0, 0, 0], [], [], [], [], [])
print(message)

