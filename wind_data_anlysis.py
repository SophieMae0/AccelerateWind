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
    angle: central direction that the wind turbine collects wind from in radians
    width: width in radians that wind can be collected with no loss, with angle
           at the center
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
    #the lower the angle difference the more power the wind generates
    angle_difference_width = angle_difference-width/2
    angle_difference = np.where(angle_difference>(2*math.pi-width/2), 0, angle_difference)
    angle_difference = np.where(angle_difference_width<0, 0, angle_difference)
    #velocity of the wind that can be collected by the turbine
    velocity_array = np.cos(angle_difference)*speed_array
    #if the velcity is negative it is turned to zero
    velocity_array = np.where(velocity_array>0, velocity_array, 0)
    #power of the wind turbine
    power_array = power_function(velocity_array)
    return [power_array,velocity_array,speed_array]

def all_angle_power(u_array,v_array,num_angles,width):
    """Inputs:
    u_array and v_array: wind vectors in the u and v directions in m/s
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
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
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    width: width in radians that wind can be collected with no loss
    Outputs:
    best_angle: with highest AEP (radians) for each coordinate
    best_energy: amount of energy (J) produced at the best angle
    """
    #power at all angles for all coordinates
    power_all_angles = all_angle_power(u_array,v_array,num_angles,width)
    #converting to energy, 60 is converting from minutes to seconds
    energy_all_angles = np.array(simps(power_all_angles))*60
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
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    width: width in radians that wind can be collected with no loss
    Outputs:
    angles: angle with highest AEP (radians) for each coordinate,
            amount of energy (J) produced the best angle
    wind_info: power, velocity and speed at the best angle
    """
    angles = best_angle_energy(u_array,v_array,num_angles,width)
    wind_info = velocity_function(u_array,v_array,angles[0],width)
    return angles,wind_info

def generator_energy(power_array,gen_size):
    """Inputs:
    power_array: power of wind turbine facing in the optimal direction
    gen_size: generator size in m/s
    Outputs:
    energy_percents: an array of the percentage energy produced at each
                     location for each different generator size
    """
    #max wind power that can be collected
    max = power_function(gen_size)
    #power_difference will be negative if power is above max
    power_difference = max - power_array
    #if power_difference is negative power is set to max
    new_power = np.where(power_difference>=0, power_array, max)
    #convert to energy (J)
    new_energy = simps(new_power)*60 #60 is converting from minutes to secnds
    #sum up energy over time
    return new_energy


def all_generators_energy(power_array,original_energy,num_gen):
    """Inputs:
    power_array: power of wind turbine facing in the optimal direction
    original_energy: how much energy would be collected if the generator
                     had no maximum
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between 6 and 12 m/s
    Outputs:
    energy_percents: an array of the percentage energy produced at each
                     location for each different generator size
    """
    energy_percents = []
    for i in range(num_gen): #number of dif sized generators
        #iterating over generators between size 6 to 12 (m/s)
        gen_energy = generator_energy(power_array,6+(i/(num_gen-1))*6)
        #percentage difference between original energy and energy with this generator
        energy_difference = gen_energy/original_energy
        energy_percents.append(energy_difference)
    #percentage difference between original energy and energy with all diferent generators
    return np.array(energy_percents)

def generator_classification(power_array,original_energy,num_gen,best_percent):
    """Inputs:
    power_array: power of wind turbine facing in the optimal direction
    original_energy: how much energy would be collected if the generator
                     had no maximum
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between 6 and 12 m/s
    best_percent: the optimal percentage of energy for a genrator to collect
    Outputs:
    best_gen_list: an array of the generator sizes that collect the closest
                   but lower than the optimal percentage of energy for each coordinate
    best_percent_list: an array of the percentages of energy that the best_gen_list
                       generators collect
    """
    #percentage of optimal energy with num_gen different genrators
    percent_all_gen = all_generators_energy(power_array,original_energy,num_gen)
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
            #if second best percent is the highest generator
            if i == num_gen-1:
                best_percent = percent_all_gen[i]
                best_gen = 6+(i/(num_gen-1))*6
            #best gen is one greater than second best
            else:
                best_percent = percent_all_gen[i+1]
                best_gen = 6+(i/(num_gen-1))*6
            above_best = False
            break
        #if all percentages are above best percent
        if above_best:
            #adding the lowest percentage
            best_percent = percent_all_gen[0]
            #adding the smallest generator
            best_gen = 6
    return best_gen,best_percent

def flywheel_energy(power_array,gen_size,fly_size):
    """Inputs:
    power_array: power of wind turbine facing in the optimal direction
    gen_size: generator size in m/s
    fly_size: fywheel size in watts
    Outputs:
    fly_energy: sum of energy that is stored in the flywheel (J)
    gen_energy: sum of energy collected by the generator (J)
    """
    #max wind power that can be collected in genertor and flywheel
    max_gen = power_function(gen_size)
    max_fly = fly_size
    #power_difference will be negative if power is below max
    power_dif = power_array - max_gen

    fly_power_list = [0] #setting orignal energy in flywheel

    for i in range(len(power_dif)): #for each time step
        #the power in the flywheel starts at the power from the end
        #of the last time step
        fly_power = fly_power_list[i]
        #putting enegry back into the generator
        if power_dif[i] < 0: #if energy is going back into the generator
            #adding the amount of power in the flyhweel into the generator
            power_array[i] += fly_power
            #subtracting the amount of power in flywheel from the generator
            fly_power += power_dif[i]
            if fly_power < 0: #if flywheel power is negative
                fly_power = 0 #set flywheel power to zero
        #changing power in flyheel
        else:
            #addingthe amount of power that exceeds the generator
            #to the flywheel
            fly_power += power_dif[i]
            if fly_power > max_fly: #if flywheel energy is higher than max
                fly_power = max_fly #set flywheel power to maximum

        fly_power_list.append(fly_power)

    #chaning any power int he genrator that exceeds the maximum to the max
    np.where(power_array>max_gen,max_gen,power_array)

    #converting to enery (J)
    fly_energy = simps(fly_power_list)*60
    gen_energy = simps(power_array)*60
    return(fly_energy,gen_energy)


def all_flywheel_gen_energy(power_array,num_gen,num_fly):
    """Inputs:
    power_array: power of wind turbine facing in the optimal direction
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between 7 and 12
    num_fly: number of different sizes a flywheel could be
    Outputs:
    gen_energy_array: array of the sums of energy collected by every
                      generator and flywheel combination
    """
    max_fly = power_function(12)
    gen_energy_array = []
    for i in range(num_gen):
        print('i is' , i)
        gen_energy_array.append([])
        for j in range(num_fly):
            print('j is' , j)
            #num gen is distributed between 6 and 12
            #num fly is distributed between the power equivilents of zero and 6 m/s
            fly_energy, gen_energy = flywheel_energy(power_array,6+(i/(num_gen-1))*6,((j+1)/(num_fly)*max_fly))
            gen_energy_array[i].append(gen_energy)
    return(np.array(gen_energy_array))

def cost_curve(energy,gen_size,flywheel_size):
    gen_size = power_function(gen_size)
    mech_cost = 1118
    inverter_rate = .35


def classification():
    pass




                ###CALCULATING VALUES FOR GRAPHS
#
# os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes10')
# width = math.pi
# x = []
# y = []
# gen_list = []
# energy_list = []
# angle_list = []
# all_angle_list = []
# power_list = []
# speed_list = []
# velocity_list = []
# flywheel_list = []
# flywheel_gen_list = []
# flywheel_gen_plain_list = []
# all_flywheel_list = []
# i = 0
# for file in glob.glob("*"): #for each file in any folder
#     i += 1
#     print(i)
#     print(file)
#     coord = eval(file)
#     u10,v10,direction = (get_data(file))
#     u10 = np.delete(u10,slice(103000,103500))
#     v10 = np.delete(v10,slice(103000,103500))
#     direction = np.delete(direction,slice(103000,103500))
#     info = coordinate_info(u10,v10,16,math.pi)
    # #
    # flywheel,flywheel_gen = flywheel_energy(info[1][0],6,6)
    # flywheel = flywheel/3 #divided by 3 to make it annual
    # flywheel_gen = flywheel_gen/3 #divided by 3 to make it annual
    # flywheel_gen_plain = generator_energy(info[1][0],6)/3

    # all_flywheel = all_flywheel_gen_energy(info[1][0],6,6)
# #
# #     # energy = info[0][1]/3 #divided by 3 so its annual
# #     # angle = info[0][0]
# #     # power = np.sum(info[1][0])/len(info[1][0])
# #     # speed = np.sum(info[1][2])/len(info[1][2])
# #     #
# #     # velocity = np.sum(info[1][1])/len(info[1][1])
# #     #
# #     # gen = generator_classification(info[1][0],info[0][1],2,.8)[0]
# #
# #
# #     # wind_angle = np.arctan2(u10, v10) + math.pi
# #     # angle_difference = abs(wind_angle - angle)
# #     # angle_difference_width = angle_difference-width/2
# #     # angle_difference = np.where(angle_difference>(2*math.pi-width/2), 1, 0)
# #     # angle_difference = np.where(angle_difference_width>0, 1, 0)
# #     # all_angle = np.sum(angle_difference)/315360
# #     # gen_list.append(gen)
# #     # energy_list.append(energy)
# #     # angle_list.append(angle)
# #     # all_angle_list.append(all_angle)
# #     # power_list.append(power)
# #     # speed_list.append(speed)
# #     # velocity_list.append(velocity)
    # flywheel_list.append(flywheel)
    # flywheel_gen_list.append(flywheel_gen)
    # flywheel_gen_plain_list.append(flywheel_gen_plain)
    # all_flywheel_list.append(all_flywheel)
#     # y.append(coord[0]-25)
#     # x.append(coord[1]+125)
#
# os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34')
# pickle.dump(all_flywheel_list,open('all_flywheel_list6p.txt', 'wb'))
# pickle.dump(flywheel_list,open('flywheel_list.txt', 'wb'))
# pickle.dump(flywheel_gen_list,open('flywheel_gen_list.txt', 'wb'))
# pickle.dump(flywheel_gen_plain_list,open('flywheel_gen_plain_list.txt', 'wb'))
# pickle.dump(gen_list,open('gen_list180.txt', 'wb'))
# pickle.dump(energy_list,open('energy_list180.txt', 'wb'))
# pickle.dump(angle_list,open('angle_list180.txt', 'wb'))
# pickle.dump(all_angle_list,open('all_angle_list180.txt', 'wb'))
# pickle.dump(power_list,open('power_list180.txt', 'wb'))
# pickle.dump(speed_list,open('speed_list180.txt', 'wb'))
# pickle.dump(velocity_list,open('velocity_list180.txt', 'wb'))
# pickle.dump(x,open('x.txt', 'wb'))
# pickle.dump(y,open('y.txt', 'wb'))
#
os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34')
flywheel_list = pickle.load(open('flywheel_list.txt', 'rb'))
flywheel_gen_list = pickle.load(open('flywheel_gen_list.txt', 'rb'))
flywheel_gen_plain_list = pickle.load(open('flywheel_gen_plain_list.txt', 'rb'))
gen_list = pickle.load(open('gen_list180.txt', 'rb'))
energy_list = np.array(pickle.load(open('energy_list180.txt', 'rb')))
angle_list = np.array(pickle.load(open('angle_list180.txt', 'rb')))
all_angle_list = np.array(pickle.load(open('all_angle_list180.txt', 'rb')))
power_list = np.array(pickle.load(open('power_list180.txt', 'rb')))
speed_list = np.array(pickle.load(open('speed_list180.txt', 'rb')))
velocity_list = np.array(pickle.load(open('velocity_list180.txt', 'rb')))
x = pickle.load(open('x.txt', 'rb'))
y = pickle.load(open('y.txt', 'rb'))



##FLYWHEEL
plt.figure(figsize = (5,20))
plt.subplot(3,1,1)
#creates scatterplot
plt.scatter(x,y,c = np.log10(flywheel_list),label = 'Weather Site',cmap ='jet')
#adds title
plt.title('Annual Energy ', fontsize = 15)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)

cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

plt.clim(7.5, 9.5);

plt.subplot(3,1,2)
plt.scatter(x,y,c = np.log10(flywheel_gen_list),label = 'Weather Site',cmap ='jet')


#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)

plt.ylabel('Latitude', fontsize = 20)

cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

cbar.set_label(label = 'Log10 of Average Annual Energy (J)', fontsize = 20)
plt.clim(7.5, 9.5);

plt.subplot(3,1,3)
plt.scatter(x,y,c = np.log10(flywheel_gen_plain_list),label = 'Weather Site',cmap ='jet')

#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)


cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

plt.clim(7.5, 9.5);
plt.show()




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
plt.title('Annual Energy', fontsize = 25)
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
plt.clim(8, 9.5);
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
plt.clim(20, 150);
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
plt.clim(1, 7);
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
plt.clim(1, 7);
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


            ###VELOCITY/SPEED
#creates scatterplot
plt.scatter(x,y,c = velocity_list/speed_list,label = 'Weather Site',cmap ='jet')
#adds title
plt.title('Velocity/Speed', fontsize = 25)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)
plt.ylabel('Latitude', fontsize = 20)
#adds legend
plt.legend(loc=3, fontsize = 15)
cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

#cbar.set_label( fontsize = 20)
plt.clim(.5,1);
plt.show()
