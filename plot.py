import matplotlib.pyplot as plt
import numpy as np

class postprocessing:
    def __init__(self,Cap,Angles,ship_name):
        
        self.Cap=Cap
        self.Angles=Angles
        self.ship_name=ship_name
    

    def polarplot(self):
        Cap=self.Cap
        Angles=self.Angles
        ship_name=self.ship_name
        
        last_DP=Cap[0]
        Angles_complete=np.append(Angles,360)
        Cap=np.append(Cap,last_DP)        
        Angles_rad=np.radians(Angles_complete)
        
        im=plt.imread('ship.png') 
        
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(10, 10))
        ax.plot(Angles_rad, Cap, color='navy', linewidth=4,alpha=0.5)
        ax.set_rmax(12)
        ax.set_rticks([0,1,2,3,4,5,6,7,8,9,10,11,12])  
        ax.set_thetagrids(Angles)
        ax.set_rlabel_position(22.5)  
        ax.grid(True)
        ax.set_theta_zero_location("N")  # theta=0 at the top
        ax.set_theta_direction(-1)  # theta increasing clockwise
        ax.set_title("DP Capability \n", va='bottom',fontsize=25, color='navy')
        
        newax = fig.add_axes([0.4387,0.443,0.15,0.15], anchor='N', zorder=1)
        newax.imshow(im,alpha=0.6)
        newax.axis('off')
        
        plt.savefig('RESULTS/'+str(ship_name)+'/DP_Cap.png', dpi=150)
    