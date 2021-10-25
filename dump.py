import numpy as np
import math as math
import pickle
import glob
import memory_profiler
import os
from scipy.integrate import simps
from matplotlib import pyplot as plt
import reverse_geocoder as rg
from collections import defaultdict
import random
from calc import *
from controls import *
import time
from time import sleep
import multiprocessing as mp

#defining global variables
i = -1

def basic_calc(folder,file,file_count):
    global i
    i += 1
    print(file)
    print(round((i*mp.cpu_count())/file_count*100,2),'% done')
    coord = eval(file) #extracting the name of the file which is a coordinate
    u10,v10,direction = (get_data(folder,file)) #extracting wind speed and direction
    u10 = np.delete(u10,slice(103000,103500)) #deleting bad data
    v10 = np.delete(v10,slice(103000,103500)) #deleting bad data

    direction = np.delete(direction,slice(103000,103500)) #deleting bad data
    #calculating best angle and energy, power, velocity and speed at that angle
    info = coordinate_info(u10,v10,num_angles,width,perp,vel_factor)
    info2 = coordinate_info(u10,v10,num_angles,2*np.pi,False,vel_factor)
    power_array = info[1][0] #list of power every 5 minutes at the best angle
    potential_power_array = info2[1][0] #list of power every 5 minutes at the best angle
    best_energy = info[0][1] #sum of energy at the best angle
    energy = best_energy/num_years #divided by 3 so its annual
    angle = info[0][0] #angle that collects the most energy
    power = np.sum(power_array)/len(power_array) #average power
    potential_power = np.sum(potential_power_array)/len(potential_power_array) #total possible power
    speed = np.sum(info[1][2])/len(info[1][2]) #average speed
    velocity = np.sum(info[1][1])/len(info[1][1]) #average velocity
    gen_energy = generator_energy(power_array,gen_size)/num_years
    cost = cost_curve(gen_size,fly_size,gen_energy)
    #reverse geocodes what state the coordinate is in
    loc = rg.search((coord[0],coord[1]),mode=1)
    state = loc[0]['admin1']

    return [coord[0],coord[1],energy,angle,power,potential_power,speed,velocity,gen_energy,cost,state]

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
    start = time.perf_counter() #statrs timer
    #redirecting to the file containing fiveMinutes data
    os.chdir(folder)

    path, dirs, files = next(os.walk(folder))
    file_count = len(files)

    #initiating multiprocessing to make the program run faster
    #takes appx 3/5 time to run as compared to single processing
    pool = mp.Pool(mp.cpu_count()) #creates a multiprocessing pool with n ccpus
        #where n is the number of cpus on the computer running the program
    #iterates through basic_calc asynchronously, with starmap infrastructure
    results = pool.starmap_async(basic_calc,[(folder,file,file_count) for file in glob.glob('*')]).get()
    print(results)

    pool.close()
    pool.join() #joins seperate processes, makes sure above part is finsihed before moving on

    results_array = np.array(results)

    x = results_array[:,0]
    y = results_array[:,1]
    energy_list = results_array[:,2]
    angle_list = results_array[:,3]
    power_list = results_array[:,4]
    potential_power_list = results_array[:,5]
    speed_list = results_array[:,6]
    velocity_list = results_array[:,7]
    gen_energy_list = results_array[:,8]
    cost_list = results_array[:,9]
    state_list = results_array[:,10]

    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt_%s.txt' % (name), 'wb'))
    pickle.dump(y,open('y.txt_%s.txt'% (name), 'wb'))
    pickle.dump(energy_list,open('energy_list_%s.txt' % (name), 'wb'))
    pickle.dump(angle_list,open('angle_list_%s.txt' % (name), 'wb'))
    pickle.dump(power_list,open('power_list_%s.txt' % (name), 'wb'))
    pickle.dump(potential_power_list,open('potential_power_list_%s.txt' % (name), 'wb'))
    pickle.dump(speed_list,open('speed_list_%s.txt' % (name), 'wb'))
    pickle.dump(velocity_list,open('velocity_list_%s.txt' % (name), 'wb'))
    pickle.dump(gen_energy_list,open('gen_energy_list_%s.txt' % (name), 'wb'))
    pickle.dump(cost_list,open('cost_list_%s.txt' % (name), 'wb'))
    pickle.dump(state_list,open('state_list_%s.txt' % (name), 'wb'))

    finish = time.perf_counter() #prints how long the function took
    print('done in',finish-start,'seconds')

if __name__ == '__main__':
    #you only need to use basic, the others are for pretty specific examples:

    #sting name of the folder the data is in
    folder = '/media/sophie/Rapid/AccelerateWind/fiveMinutes10'
    #small data set is fiveMinutes10
    #big data set is TestDataPred

    #string that was used to label the files when loading them
    name = 'paralell test'

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

    dump_pickles_basic(folder,name,width,num_angles,gen_size,fly_size,perp,vel_factor)
