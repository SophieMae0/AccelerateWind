import xarray as xr
import cfgrib
import numpy as np
import math as math
import pickle
import glob
import memory_profiler
import os
from matplotlib import pyplot as plt
from scipy.integrate import simps

ro=1.225 #kg/m3 density of air
cp = .35 #coefficient of performance
radius = 1 #radius in meters
area = math.pi*(radius**2) #area in meters squared

#waterMask.txt is a binary txt
#0 is water and 1 is land
#360 columns  = 360 degrees longitude (-180 to 180)
#180 rows = 180 degrees latitude (90 to -90)
file = open('waterMask.txt', 'r')
water_binary_strings = []
#splits waterMask into 180 lists of length 360
for line in file:
    water_binary_strings.append(line.split())

def get_data(file_name):
    data = np.memmap('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes10/%s' % (file_name),mode='r+',dtype='float32',shape=(315360,2))
    speed = np.array(data[:,0])
    direction = np.array(data[:,1])
    direction = 2*math.pi*direction/360 #converting to radians
    u_array = speed*np.sin(direction) #north/south
    v_array = speed*np.cos(direction)
    return u_array, v_array, direction

def speed_function(u_array,v_array):
    """Input: wind vectors in the u and v directions in m/s
    Output: wind speed in m/s"""
    speed_array = np.sqrt((u_array**2)+(v_array**2))
    return speed_array

def power_function(speed_array):
    """Input: wind speed m/s
    Output: power in J/s"""
    power_array= .5*ro*cp*area*(np.power(speed_array,3))
    return power_array

##EVERYTHING IS IN RADIANS
#zero radians is wind going exactly west
def velocity_function(u_array,v_array,angle,width):
    """Inputs:
    u_array and v_array: wind vectors in the u and v directions in m/s
    angle: angle that the wind turbine collects wind from
    width: width in radians that wind can be collected with no loss
    Outputs:
    power_array: power of turbine (W) collecting wind from angle direction
    velocity_array: wind velocity (m/s) that is collected by the tubine
    speed_array: speed of wind (m/s)"""
    speed_array = speed_function(u_array,v_array)
    #angle in radians that the wind is blowing towards
    wind_angle = np.arctan2(u_array,v_array)+math.pi #making scale from 0 to 2pi
    #difference between wind direction and the angle the turbine is facing
    angle_difference = abs(wind_angle - angle)
    #no loss of speed if angle difference is within specified width
    angle_difference_width = angle_difference-width/2
    angle_difference = np.where(angle_difference>(2*math.pi-width/2), 0, angle_difference)
    angle_difference = np.where(angle_difference_width>0, angle_difference, 0)
    #velocity of the wind that can be collected by the turbine
    velocity_array = np.cos(angle_difference)*speed_array
    #if the velcity is negative it is turned to zero
    velocity_array = np.where(velocity_array>0, velocity_array, 0)
    #power of the wind turbine
    power_array = power_function(velocity_array)
    #print('power',power_array)
    return [power_array,velocity_array,speed_array]

def all_angle_power(u_array,v_array,num_angles,width):
    """Inputs:
    u_array and v_array: wind vectors in the u and v directions in m/s
    angle: angle that the wind turbine collects wind from
    width: width in radians that wind can be collected with no loss
    Outputs: power of turbine facing num_angles different directions
    """
    power_angle_list = []
    for i in range(num_angles): #for each angle
        #calculates power of turbine
        power_angle_list.append(velocity_function(u_array,v_array,2*math.pi*(i/num_angles),width)[0])
    return np.array(power_angle_list)

def best_angle_energy(u_array,v_array,num_angles,width):
    """Inputs:
    u_array and v_array: wind vectors in the u and v directions in m/s
    angle: angle that the wind turbine collects wind from
    width: width in radians that wind can be collected with no loss
    Outputs:
    angle_matrix: angle with highest AEP (radians) for each coordinate
    best_energy: amount of energy (J) produced at each best angle
    """
    #power at all angles for all coordinates
    power_all_angles = all_angle_power(u_array,v_array,num_angles,width)
    #converting to energy
    energy_all_angles = np.array(simps(power_all_angles))
    #determining which angle at each turbine produces the most energy
    best_energy = np.max(energy_all_angles)
    #creating an array of best angle per coordinate
    angle_matrix = []
    for i in range(len(energy_all_angles)):
    #if the energy at this angle equals the maximum energy possible
        if energy_all_angles[i] == best_energy:
            #add this angle as the best angle for this coordinate
            best_angle = 2*math.pi*(i/num_angles)
            break #has preference towards lower angles
    return best_angle,best_energy

def coordinate_info(u_array,v_array,num_angles,width):
    """Inputs:
    u_array and v_array: wind vectors in the u and v directions in m/s
    angle: angle that the wind turbine collects wind from
    width: width in radians that wind can be collected with no loss
    Outputs:
    angle_matrix: angle with highest AEP (radians) for each coordinate
    best_energy: amount of energy (J) produced at each best angle
    """
    angles = best_angle_energy(u_array,v_array,num_angles,width)
    wind_info = velocity_function(u_array,v_array,angles[0],width)
    return angles,wind_info

def all_generators_energy(u_array,v_array,num_angles,width,num_gen):
    """Inputs:
    u_array and v_array: wind vectors in the u and v directions in m/s
    angle: angle that the wind turbine collects wind from
    width: width in radians that wind can be collected with no loss
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between 7 and 12
    Outputs:
    energy_list: an array of the percentage energy produced at each
                 location for each different generator size
    """
    info = coordinate_info(u_array,v_array,num_angles,width)
    power_array = info[1][0] #power collected at optimal angle
    original_energy = info[0][1] #energy collected with no gen limit
    energy_percents = []
    for i in range(num_gen): #number of dif sized generators
        #max wind power that can be collected
        max = power_function(6+(i/num_gen)*6) #max wind speeds between 7 and 12 m/s
        #power_difference will be negative if power is above max
        power_difference = max - power_array
        #if power_difference is negative power is set to max
        new_power = np.where(power_difference>=0, power_array, max)
        #convert to energy (J)
        new_energy = simps(new_power)
        #sum up energy over time
        new_energy_total = np.sum(new_energy,0)
        #percentage difference between original energy and energy with this generator
        energy_difference = np.where(original_energy == 0, 0,new_energy_total/original_energy)
        energy_percents.append(energy_difference)
    #percentage difference between original energy and energy with all diferent generators
    return np.array(energy_percents)

def generator_classification(u_array,v_array,num_angles,width,num_gen,best_percent):
    """Inputs:
    u_array and v_array: wind vectors in the u and v directions in m/s
    angle: angle that the wind turbine collects wind from
    width: width in radians that wind can be collected with no loss
    num_gen: number of different sizes a generator could be
             the sizs are equally distributed between 7 and 12
    best_percent: the optimal percentage of energy for a genrator to collect
    Outputs:
    best_gen_list: an array of the generator sizes that collect the closest
                   but lower than the optimal percentage of energy for each coordinate
    best_percent_list: an array of the percentages of energy that the best_gen_list
                       generators collect
    """
    #percentage of optimal energy with num_gen different genrators
    percent_all_gen = all_generators_energy(u_array,v_array,num_angles,width,num_gen)
    #all percentages higher than best_percent are zero
    percent_below = np.where(percent_all_gen>=best_percent,0,percent_all_gen)
    #determining which generator is closest and lower than best_percent
    second_best_percent = np.max(percent_below,0)
    best_gen = [] #generator size
    best_percent = [] #percentage of optimal energy produces with that generator

    for i in range(num_gen): #generator size
        above_best = True #true if all percentages are above best percentage
        #if the current percentage equals the second best percentage for that coordinate
        if percent_all_gen[i] == second_best_percent:
            #checking for water
            if second_best_percent == 0:
                #setting water coordinates to 0
                best_percent = 0
                best_gen = 0
            #if second best percent is the highest generator
            elif i == num_gen-1:
                best_percent = percent_all_gen[i]
                best_gen = 6+((i)/num_gen)*6
            #best gen is one greater than second best
            else:
                best_percent = percent_all_gen[i+1]
                best_gen = 6+((i+1)/num_gen)*6
            above_best = False
            break
        #if all percentages are above best percent
        if above_best:
            #adding the lowest percentage
            best_percent = percent_all_gen[0]
            #adding the smallest generator
            best_gen = 6+((0)/num_gen)*6
    return best_gen,best_percent

def weibull_distribution(u_array,v_array,num_angles,width):
    speed_array = coordinate_info(u_array,v_array,num_angles,width)[1][2]
    speed_array = np.floor(speed_array)

    speed_dict_list = []
    for i in range(len(percent_all_gen[0,:,0])): #latitude
        dict_list.append([])
        for j in range(len(percent_all_gen[0,0,:])): #longitude
            unique, counts = numpy.unique(speed_array[:,i,j], return_counts=True)
            speed_dict = dict(zip(unique, counts))
            speed_dict_list.append(speed_dict)


                ###CALCULATING VALUES FOR GRAPHS

os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes10')
width = math.pi
x = []
y = []
gen_list = []
energy_list = []
angle_list = []
all_angle_list = []
power_list = []
speed_list = []
velocity_list = []
i = 0
for file in glob.glob("*"): #for each file in any folder
    i += 1
    print(i)
    coord = eval(file)
    u10,v10,direction = (get_data(file))
    u10 = np.delete(u10,slice(103000,103500))
    v10 = np.delete(v10,slice(103000,103500))
    direction = np.delete(direction,slice(103000,103500))
    gen = generator_classification(u10,v10,16,2*math.pi,10,.8)[0]
    info = coordinate_info(u10,v10,16,2*math.pi)
    energy = info[0][1] #divided by 3 so its annual
    angle = info[0][0]
    power = np.sum(info[1][0])/len(info[1][0])
    speed = np.sum(info[1][2])/len(info[1][2])
    velocity = np.sum(info[1][1])/len(info[1][1])
    #print(angle)
    wind_angle = np.arctan2(u10, v10) + math.pi
    angle_difference = abs(wind_angle - angle)
    #print(angle_difference)
    angle_difference_width = angle_difference-width/2
    angle_difference = np.where(angle_difference>(2*math.pi-width/2), 1, 0)
    angle_difference = np.where(angle_difference_width>0, 1, 0)
    all_angle = np.sum(angle_difference)/315360
    gen_list.append(gen)
    energy_list.append(energy)
    angle_list.append(angle)
    all_angle_list.append(all_angle)
    power_list.append(power)
    speed_list.append(speed)
    velocity_list.append(velocity)
    y.append(coord[0]-25)
    x.append(coord[1]+125)

os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34')
pickle.dump(gen_list,open('gen_list.txt', 'wb'))
pickle.dump(energy_list,open('energy_list.txt', 'wb'))
pickle.dump(angle_list,open('angle_list.txt', 'wb'))
pickle.dump(all_angle_list,open('all_angle_list.txt', 'wb'))
pickle.dump(power_list,open('power_list.txt', 'wb'))
pickle.dump(speed_list,open('speed_list.txt', 'wb'))
pickle.dump(velocity_list,open('velocity_list.txt', 'wb'))
pickle.dump(x,open('x.txt', 'wb'))
pickle.dump(y,open('y.txt', 'wb'))

os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34')
gen_list = pickle.load(open('gen_list.txt', 'rb'))
energy_list = np.array(pickle.load(open('energy_list.txt', 'rb')))
angle_list = np.array(pickle.load(open('angle_list.txt', 'rb')))
all_angle_list = np.array(pickle.load(open('all_angle_list.txt', 'rb')))
power_list = np.array(pickle.load(open('power_list.txt', 'rb')))
speed_list = np.array(pickle.load(open('speed_list.txt', 'rb')))
velocity_list = np.array(pickle.load(open('velocity_list.txt', 'rb')))
x = pickle.load(open('x.txt', 'rb'))
y = pickle.load(open('y.txt', 'rb'))

####GENERATOR SIZE

#creates scatterplot
plt.scatter(x,y,c = gen_list,label = 'Weather Site',cmap ='jet')
#adds title
plt.title('Generator Size that Collects 80 Percent of Energy', fontsize = 25)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)
plt.ylabel('Latitude', fontsize = 20)
#adds legend
plt.legend(loc=3, fontsize = 15)
cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

cbar.set_label(label = 'Generator Size (m/s)', fontsize = 20)
plt.clim(6, 12);
plt.show()


            #####ENERGY

#creates scatterplot
plt.scatter(x,y,c = np.log10(energy_list),label = 'Weather Site',cmap ='jet')
#adds title
plt.title('Energy Production in a Year', fontsize = 25)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)
plt.ylabel('Latitude', fontsize = 20)
#adds legend
plt.legend(loc=3, fontsize = 15)
cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

cbar.set_label(label = 'Log10 of Average Annual Energy (J)', fontsize = 20)
plt.clim(6.5, 8.5);
plt.show()


            #####POWER

#creates scatterplot
plt.scatter(x,y,c = power_list,label = 'Weather Site',cmap ='jet')
#adds title
plt.title('Average Power', fontsize = 25)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)
plt.ylabel('Latitude', fontsize = 20)
#adds legend
plt.legend(loc=3, fontsize = 15)
cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

cbar.set_label(label = 'Power (W)', fontsize = 20)
plt.clim(10, 130);
plt.show()


            #####SPEED

#creates scatterplot
plt.scatter(x,y,c = speed_list,label = 'Weather Site',cmap ='jet')
#adds title
plt.title('Average Speed', fontsize = 25)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)
plt.ylabel('Latitude', fontsize = 20)
#adds legend
plt.legend(loc=3, fontsize = 15)
cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

cbar.set_label(label = 'Speed (m/s)', fontsize = 20)
plt.clim(2, 7);
plt.show()


            #####VELOCITY

#creates scatterplot
plt.scatter(x,y,c = velocity_list,label = 'Weather Site',cmap ='jet')
#adds title
plt.title('Average Velocity', fontsize = 25)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)
plt.ylabel('Latitude', fontsize = 20)
#adds legend
plt.legend(loc=3, fontsize = 15)
cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

cbar.set_label(label = 'Velocity (m/s)', fontsize = 20)
plt.clim(1, 6);
plt.show()


                ####ANGLES
u_array = np.sin(angle_list) #north/south
v_array = np.cos(angle_list) #east/west

#creates scatterplot
plt.quiver(x,y, u_array, v_array, scale = (1-all_angle_list)*100)
#adds title
plt.title('Wind Angle', fontsize = 25)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)
plt.ylabel('Latitude', fontsize = 20)
#adds legend
#plt.legend(loc=3, fontsize = 15)

plt.show()
