import numpy as np
import math as math
import pickle
import glob
import memory_profiler
import os
from scipy.integrate import simps
from matplotlib import pyplot as plt
import reverse_geocoder as rg
import dill
from collections import defaultdict
import random
from calc import *
from controls import *


def dump_pickles_one_gen(name,width,num_angles,gen_min,gen_max,best_percent,num_gen,fly_size,perp=False,vel_factor=1):
    """pickles generator sizes that capture optimal energy lists
    Inputs: name: string that was used to label the files when loading them
    width: width in radians that wind can be collected with no loss
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    gen_min: max wind speed the min generator could capture in m/s
    gen_max: max wind speed the min generator could capture in m/s
    best_percent: the optimal percentage of energy for a genrator to collect
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between gen_min and gen_max m/s
    vel_factor: multiplied by the velocity (can be increased to mimic rooftop speeds)
    """
    #redirecting to the file containing fiveMinutes data
    os.chdir('/media/sophie/Rapid/AccelerateWind/fiveMinutes10')
    #initilizing all the differnt lists of data
    #these are lists containing data point per coordinate
    x = []
    y = []
    gen_list = []
    percent_list = []
    energy_list = []
    i = 0 #sets file counter to 0
    for file in glob.glob("*"): #for each file in any folder
        i += 1 #increases file counter
        print('file number:', i) #prints file number the loop is currently analyzing
        print('coordinate:', file) #prints coordinate the loop is currenting analyzing
        coord = eval(file) #extracting the name of the file which is a coordinate
        u10,v10,direction = (get_data(file)) #extracting wind speed and direction
        u10 = np.delete(u10,slice(103000,103500)) #deleting bad data
        v10 = np.delete(v10,slice(103000,103500)) #deleting bad data
        #generator size that collects lower than but closest to the best percent of energy
        info = coordinate_info(u10,v10,num_angles,width,perp,vel_factor)
        power_array = info[1][0] #list of power every 5 minutes at the best angle
        best_energy = info[0][1] #sum of energy at the best angle
        energy = best_energy/num_years #divided by 3 so its annual
        gen,percent = generator_classification(power_array,best_energy,gen_min,gen_max,num_gen,best_percent,fly_size)
        energy = flywheel_energy(power_array,gen,fly_size)
        #adding the data point for this coordinate to the list containing
        gen_list.append(gen)
        percent_list.append(percent)
        energy_list.append(energy)
        y.append(coord[0])
        x.append(coord[1])

        # print(gen)

    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt', 'wb'))
    pickle.dump(y,open('y.txt', 'wb'))
    pickle.dump(gen_list,open('gen_list_%s.txt' % (name), 'wb'))
    pickle.dump(percent_list,open('percent_list_%s.txt' % (name), 'wb'))
    pickle.dump(energy_list,open('energy_list_%s.txt' % (name), 'wb'))

def dump_pickles_one_fly(name,width,num_angles,gen_size,fly_size,perp=False,vel_factor=1):
    """pickles flywheel and generator annual energy lists
    Inputs: name: string that was used to label the files when loading them
    width: width in radians that wind can be collected with no loss
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    gen_size: size of gen in (m/s) the generator could capture
    fly_size: ammount time (s) a 12 m/s wind would have to blow to fill the flywheel
    vel_factor: multiplied by the velocity (can be increased to mimic rooftop speeds)
    """
    #redirecting to the file containing fiveMinutes data
    os.chdir('/media/sophie/Rapid/AccelerateWind/fiveMinutes10')
    #initilizing all the differnt lists of data
    #these are lists containing data point per coordinate
    x = []
    y = []
    flywheel_gen_list = []
    flywheel_gen_plain_list = []
    i = 0 #sets file counter to 0
    for file in glob.glob("*"): #for each file in any folder
        i += 1 #increases file counter
        print('file number:', i) #prints file number the loop is currently analyzing
        print('coordinate:', file) #prints coordinate the loop is currenting analyzing
        coord = eval(file) #extracting the name of the file which is a coordinate
        u10,v10,direction = (get_data(file)) #extracting wind speed and direction
        u10 = np.delete(u10,slice(103000,103500)) #deleting bad data
        v10 = np.delete(v10,slice(103000,103500)) #deleting bad data
        #calculating best angle and energy, power, velocity and speed at that angle
        info = coordinate_info(u10,v10,num_angles,width,perp,vel_factor)
        power_array = info[1][0] #list of power every 5 minutes at the best angle
        flywheel_gen = flywheel_energy(power_array,power_function(gen_size),fly_size*power_function(12))
        flywheel_gen = flywheel_gen/num_years #divided by 3 to make it annual
        flywheel_gen_plain = generator_energy(power_array,gen_size)/num_years
        #adding the data point for this coordinate to the list containing

        flywheel_gen_list.append(flywheel_gen)
        flywheel_gen_plain_list.append(flywheel_gen_plain)
        y.append(coord[0])
        x.append(coord[1])

    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt', 'wb'))
    pickle.dump(y,open('y.txt', 'wb'))
    pickle.dump(flywheel_gen_list,open('flywheel_gen_list_%s.txt' % (name), 'wb'))
    pickle.dump(flywheel_gen_plain_list,open('flywheel_gen_plain_list_%s.txt' % (name), 'wb'))

def dump_pickles_cost(name,width,num_angles,gen_min,gen_max,fly_min,fly_max,num_fly,num_gen,perp=False,vel_factor=1):
    """pickles lowest costs lists and their generator and flywheel sizes
    Inputs: name: string that was used to label the files when loading them
    width: width in radians that wind can be collected with no loss
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    gen_min: max wind speed (m/s) the min generator could capture
    gen_max: max wind speed (m/s) the min generator could capture
    fly_min: ammount time (s) a 12 m/s wind would have to blow to fill max flywheel
    fly_max: amount time (s) a 12 m/s wind would have to blow to fill min flywheel
    num_fly: number of different sizes a flywheel could be
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between 7 and 12
    vel_factor: multiplied by the velocity (can be increased to mimic rooftop speeds)
    """
    #redirecting to the file containing fiveMinutes data
    os.chdir('/media/sophie/Rapid/AccelerateWind/fiveMinutes10')
    #initilizing all the differnt lists of data
    #these are lists containing data point per coordinate
    x = []
    y = []
    low_cost_list = []
    best_gen_size_list = []
    best_fly_size_list = []
    i = 0 #sets file counter to 0
    for file in glob.glob("*"): #for each file in any folder
        i += 1 #increases file counter
        print('file number:', i) #prints file number the loop is currently analyzing
        print('coordinate:', file) #prints coordinate the loop is currenting analyzing
        coord = eval(file) #extracting the name of the file which is a coordinate
        u10,v10,direction = (get_data(file)) #extracting wind speed and direction
        u10 = np.delete(u10,slice(103000,103500)) #deleting bad data
        v10 = np.delete(v10,slice(103000,103500)) #deleting bad data
        info = coordinate_info(u10,v10,num_angles,width,perp,vel_factor)
        power_array = info[1][0] #list of power every 5 minutes at the best angle
        all_flywheel = all_flywheel_gen_energy(power_array,gen_min,gen_max,fly_min,fly_max,num_gen,num_fly)
        low_cost,best_gen_size,best_fly_size = best_cost(gen_min,gen_max,fly_min,fly_max,num_gen,num_fly,all_flywheel)
        #adding the data point for this coordinate to the list containing
        low_cost_list.append(low_cost)
        best_gen_size_list.append(best_gen_size)
        best_fly_size_list.append(best_fly_size)
        y.append(coord[0])
        x.append(coord[1])

    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt', 'wb'))
    pickle.dump(y,open('y.txt', 'wb'))
    pickle.dump(low_cost_list,open('low_cost_list_%s.txt' % (name), 'wb'))
    pickle.dump(best_gen_size_list,open('best_gen_size_list_%s.txt' % (name), 'wb'))
    pickle.dump(best_fly_size_list,open('best_fly_size_list_%s.txt' % (name), 'wb'))

def dump_pickles_storage(name,width,num_angles,gen_size,perp=False,vel_factor=1,solar_size=350,solar_area=2,solar_eff=.5):
    """pickles flywheel and generator annual energy lists
    Inputs: name: string that was used to label the files when loading them
    width: width in radians that wind can be collected with no loss
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    gen_size: size of gen in (W) the generator could captures
    vel_factor: multiplied by the velocity (can be increased to mimic rooftop speeds)
    solar_size: power the solar panel can take in (W)
    solar_area: size of solar panel (m)
    solar_eff: solar efficency
    """
    #redirecting to the file containing fiveMinutes data
    os.chdir('/media/sophie/Rapid/AccelerateWind/fiveMinutes10')
    #initilizing all the differnt lists of data
    #these are lists containing data point per coordinate
    x = []
    y = []
    wind_power_list = []
    solar_power_list = []

    i = 0 #sets file counter to 0
    for file in glob.glob("*"): #for each file in any folder
        i += 1 #increases file counter
        print('file number:', i) #prints file number the loop is currently analyzing
        print('coordinate:', file) #prints coordinate the loop is currenting analyzing
        coord = eval(file) #extracting the name of the file which is a coordinate
        u10,v10,direction = (get_data(file)) #extracting wind speed and direction
        u10 = np.delete(u10,slice(103000,103500)) #deleting bad data
        v10 = np.delete(v10,slice(103000,103500)) #deleting bad data

        direction = np.delete(direction,slice(103000,103500)) #deleting bad data
        #calculating best angle and energy, power, velocity and speed at that angle
        info = coordinate_info(u10,v10,num_angles,width,perp,vel_factor)
        power_array = info[1][0] #list of power every 5 minutes at the best angle
        power_array = np.where(power_array>gen_size,gen_size,power_array)

        #solar data is taken every half houe
        irr = np.memmap('/media/sophie/Rapid/AccelerateWind/solarEnergyFinal/%s' % (file),mode='r+',dtype='float32',shape=(17520*3))
        irr = np.delete(irr,slice(int((103000+2)/6),int(103500/6))) #deleting bad data
        solar_power = solar_power = irr * solar_area * solar_eff
        solar_power = np.where(solar_power>solar_size,solar_size,solar_power)

        ## TODO: add controls alg
        wind = power_array
        solar = solar_power
        size = 3600000*10 #10 kwh
        low = 3600000
        high = 3600000*9
        bat,dis = battery(wind,solar,size,low,high)

        #adding the data point for this coordinate to the list containing
        y.append(coord[0])
        x.append(coord[1])
        wind_power_list.append(power_array)
        solar_power_list.append(solar_power)

    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt', 'wb'))
    pickle.dump(y,open('y.txt', 'wb'))
    pickle.dump(wind_power_list,open('wind_power_%s.txt' % (name), 'wb'))
    pickle.dump(solar_power_list,open('solar_power_list_%s.txt' % (name), 'wb'))


def dump_pickles_basic(folder,name,width,num_angles,gen_size,fly_size,perp=False,vel_factor=1):
    """pickles flywheel and generator annual energy lists
    Inputs: folder: sting name of the folder the data is in
    name: string that was used to label the files when loading them
    width: width in radians that wind can be collected with no loss
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    gen_size: size of gen in (m/s) the generator could capture
    fly_size: ammount time (s) a 12 m/s wind would have to blow to fill the flywheel
    vel_factor: multiplied by the velocity (can be increased to mimic rooftop speeds)
    perp: True when the turbine can only collect direct wind
          False when the turbine can collect all wind in width
    """
    #redirecting to the file containing fiveMinutes data
    os.chdir(file)
    #initilizing all the differnt lists of data
    #these are lists containing data point per coordinate
    x = []
    y = []
    energy_list = []
    angle_list = []
    power_list = []
    power2_list = []
    speed_list = []
    velocity_list = []
    gen_energy_list = []
    cost_list = []

    power2_list = []

    x_state = defaultdict(list)
    y_state = defaultdict(list)
    speed_state = defaultdict(list)
    velocity_state = defaultdict(list)
    power_state = defaultdict(list)
    power2_state = defaultdict(list)

    i = 0 #sets file counter to 0
    for file in glob.glob("*"): #for each file in any folder
        i += 1 #increases file counter
        print('file number:', i) #prints file number the loop is currently analyzing
        print('coordinate:', file) #prints coordinate the loop is currenting analyzing
        coord = eval(folder) #extracting the name of the file which is a coordinate
        u10,v10,direction = (get_data(file)) #extracting wind speed and direction
        u10 = np.delete(u10,slice(103000,103500)) #deleting bad data
        v10 = np.delete(v10,slice(103000,103500)) #deleting bad data

        direction = np.delete(direction,slice(103000,103500)) #deleting bad data
        #calculating best angle and energy, power, velocity and speed at that angle
        info = coordinate_info(u10,v10,num_angles,width,perp,vel_factor)
        info2 = coordinate_info(u10,v10,num_angles,2*np.pi,False,vel_factor)
        power_array = info[1][0] #list of power every 5 minutes at the best angle
        power2_array = info2[1][0] #list of power every 5 minutes at the best angle
        best_energy = 1#info[0][1] #sum of energy at the best angle
        energy = 1#best_energy/num_years #divided by 3 so its annual
        angle = info[0][0] #angle that collects the most energy
        power = np.sum(power_array)/len(power_array) #average power
        power2 = np.sum(power2_array)/len(power2_array) #total possible power
        speed = np.sum(info[1][2])/len(info[1][2]) #average speed
        velocity = np.sum(info[1][1])/len(info[1][1]) #average velocity
        gen_energy = 1#generator_energy(power_array,gen_size)/num_years
        cost = 1#cost_curve(gen_size,fly_size,gen_energy)

        #adding the data point for this coordinate to the list containing
        energy_list.append(energy)
        angle_list.append(angle)
        power_list.append(power)
        power2_list.append(power2)
        speed_list.append(speed)
        velocity_list.append(velocity)
        gen_energy_list.append(gen_energy)
        cost_list.append(cost)
        y.append(coord[0])
        x.append(coord[1])

        #adding to state dictionaries
        loc = rg.search((coord[0],coord[1]))
        state = loc[0]['admin1']
        x_state[state].append(coord[1])
        y_state[state].append(coord[0])
        speed_state[state].append(speed)
        velocity_state[state].append(velocity)
        power_state[state].append(power)
        power2_state[state].append(power2)


    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt', 'wb'))
    pickle.dump(y,open('y.txt', 'wb'))
    pickle.dump(energy_list,open('energy_list_%s.txt' % (name), 'wb'))
    pickle.dump(angle_list,open('angle_list_%s.txt' % (name), 'wb'))
    pickle.dump(power_list,open('power_list_%s.txt' % (name), 'wb'))
    pickle.dump(power2_list,open('power2_list_%s.txt' % (name), 'wb'))
    pickle.dump(speed_list,open('speed_list_%s.txt' % (name), 'wb'))
    pickle.dump(velocity_list,open('velocity_list_%s.txt' % (name), 'wb'))
    pickle.dump(gen_energy_list,open('gen_energy_list_%s.txt' % (name), 'wb'))
    pickle.dump(cost_list,open('cost_list_%s.txt' % (name), 'wb'))

    dill.dump(x_state,open('x_state_%s.txt' % (name), 'wb'))
    dill.dump(y_state,open('y_state_%s.txt' % (name), 'wb'))
    dill.dump(speed_state,open('speed_state_%s.txt' % (name), 'wb'))
    dill.dump(velocity_state,open('velocity_state_%s.txt' % (name), 'wb'))
    dill.dump(power_state,open('power_state_%s.txt' % (name), 'wb'))
    dill.dump(power2_state,open('power2_state_%s.txt' % (name), 'wb'))

if __name__ == '__main__':
    #you only need to use basic, the others are for pretty specific examples:

    #sting name of the folder the data is in
    folder = '/media/sophie/Rapid/AccelerateWind/TestDataPred'

    #string that was used to label the files when loading them
    name = 'state_big180'

    #width in radians that wind can be collected with no loss
    width = np.pi

    # number of different angles the wind turbine could be facing
    # (equally distributed around a 2 pi radian circle)
    num_angles = 8

    #size of gen in (m/s) the generator could capture
    gen_size = reverse_power_function(5000)

    #ammount time (s) a 12 m/s wind would have to blow to fill the flywheel
    fly_size = 0

    # True when the turbine can only collect direct wind
    # False when the turbine can collect all wind in width
    perp = False

    #multiplied by the velocity (can be increased to mimic rooftop speeds)
    vel_factor = 1.5

    dump_pickles_basic(file,name,width,num_angles,gen_size,fly_size,perp,vel_factor)
