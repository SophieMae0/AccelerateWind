import numpy as np
import math as math
import pickle
import glob
import memory_profiler
import os
from scipy.integrate import simps
from matplotlib import pyplot as plt

ro=1.225 #kg/m3 density of air
cp = .35 #coefficient of performance
radius = 1 #radius in meters
area = math.pi*(radius**2) #area in meters squared
num_years = 3 #number of years data has been collected

def get_data(file_name):
    """reads memory mapped file saves wind speed and direction from it
    Inputs: file_name: the name of the file
    Outputs: u_array: array wind speed (m/s) in north to south direction taken every 5 minutes
    v_array: array wind speed (m/s) in east to west direction taken every 5 minutes
    direction: array of wind direction (radians) taken every 5 minutes
               zero radians is the wind blowing exactly west
    """
    data = np.memmap('/media/sophie/Samples - 1TB/AccelerateWind/fiveMinutes10/%s' % (file_name),mode='r+',dtype='float32',shape=(315360,2))
    speed = np.array(data[:,0])
    direction = np.array(data[:,1])
    direction = 2*math.pi*direction/360 #converting to radians
    u_array = speed*np.sin(direction) #north/south
    v_array = speed*np.cos(direction) #east/west
    return u_array, v_array, direction

def speed_function(u_array,v_array):
    """calculates speed
    Input: wind vectors in the u and v directions in m/s
    Output: wind speed in m/s"""
    speed_array = np.sqrt((u_array**2)+(v_array**2))
    return speed_array

def power_function(speed_array):
    """calculates power
    Input: wind speed m/s
    Output: power in Watts"""
    power_array= .5*ro*cp*area*(np.power(speed_array,3))
    return power_array

def energy_function(power_array):
    """calculates energy
    Input: power in Watts
    Output: energy in J"""
    #creating the x coordinates that coorespond with each power value
    x = 5*np.arange(0,314860) #314860 data points each 5 minutes apart
    #converting to energy, 60 is converting from minutes to seconds
    energy = np.array(simps(power_array,x))*60
    return energy

def velocity_function(u_array,v_array,angle,width):
    """calculates the veclocty of the wind an angled turbine would collect
    and how much power that turbine would collect
    Inputs:
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
    """calculates the power a turbine will collect when facing num_angles different
    directions and can collect wind without loss over a range of width radians
    Inputs:
    u_array and v_array: wind vectors in the u and v directions in m/s
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    width: width in radians that wind can be collected with no loss
    Outputs: power of turbine facing num_angles different directions
    """
    power_angle_list = [] #creates a list that will contain power at each angle
    for i in range(num_angles): #for each angle
        #calculates power of turbine
        power_angle_list.append(velocity_function(u_array,v_array,2*math.pi*(i/num_angles),width)[0])
    return np.array(power_angle_list)

def best_angle_energy(u_array,v_array,num_angles,width):
    """calculates the optimal angle for a wind turbine to face and the annual
    energy having a wind turbine facing that direction would collect
    Inputs:
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
    #calculting total energy for a turbine pointing at each angle
    energy_all_angles = energy_function(power_all_angles)
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
    """used for grouping all important information together and
    calling many smaller functions
    Inputs:
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
    """caluclates the annual energy a wind turbine with a generator of
    gen_size would produce
    Inputs:
    power_array: power of wind turbine facing in the optimal direction in Watts
    gen_size: max wind speed (m/s) the generator could capture
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
    new_energy = energy_function(new_power)
    return new_energy


def all_generators_energy(power_array,original_energy,gen_min,gen_max,num_gen):
    """calculates the percentage of possible energy each of the num_gen generators
    ranging from gen_min to gen_max collect
    Inputs:
    power_array: power of wind turbine facing in the optimal direction in Watts
    original_energy: how much energy would be collected if the generator
                     had no maximum in J
    gen_min: max wind speed the min generator could capture in m/s
    gen_max: max wind speed the min generator could capture in m/s
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between gem_min and gen_max m/s
    Outputs:
    energy_percents: an array of the percentage energy produced at each
                     location for each different generator size
    """
    #creating a list that will contain the percentage of possible energy each
    #generator size collects
    energy_percents = []
    for i in range(num_gen): #number of dif sized generators
        #iterating over generators between size min_gen to max_gen (m/s)
        gen_energy = generator_energy(power_array,gen_min+(i/(num_gen-1))*(gen_max-gen_min))
        #percentage of original energy this generator collects
        energy_difference = gen_energy/original_energy
        energy_percents.append(energy_difference)
    #percentage difference between original energy and energy with all diferent generators
    return np.array(energy_percents)

def generator_classification(power_array,original_energy,gen_min,gen_max,num_gen,best_percent):
    """classifying each weather location to an optimum generator size that collects the closest
    best_percent of the possible energy at that weather site
    Inputs:
    power_array: power of wind turbine facing in the optimal direction in Watts
    original_energy: how much energy would be collected if the generator
                     had no maximum in J
    gen_min: max wind speed the min generator could capture in m/s
    gen_max: max wind speed the min generator could capture in m/s
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between gen_min and gen_max m/s
    best_percent: the optimal percentage of energy for a genrator to collect
    Outputs:
    best_gen_list: an array of the generator sizes (in m/s) that collect the closest
                   but lower than the optimal percentage of energy for each coordinate
    best_percent_list: an array of the percentages of energy that the best_gen_list
                       generators collect
    """
    #percentage of optimal energy with num_gen different genrators
    percent_all_gen = all_generators_energy(power_array,original_energy,gen_min,gen_max,num_gen)
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
                best_gen = gen_min+(i/(num_gen-1))*(gen_max-gen_min)
            #best gen is one greater than second best
            else:
                best_percent = percent_all_gen[i+1]
                best_gen = gen_min+(i/(num_gen-1))*(gen_max-gen_min)
            above_best = False
            break
        #if all percentages are above best percent
        if above_best:
            #adding the lowest percentage
            best_percent = percent_all_gen[0]
            #adding the smallest generator
            best_gen = gen_min
    return best_gen,best_percent

def flywheel_energy(power_array,max_gen,max_fly):
    """calculates the energy a generator of max_gen size with a flywheel of max_fly
    size could collect
    Inputs:
    power_array: power of wind turbine facing in the optimal direction in watts
    gen_size: generator size in Watts
    fly_size: flywheel size in J
    Outputs:
    gen_energy: sum of energy collected by the generator in J
    """
    #power_difference will be negative if power is below max
    power_dif = power_array - max_gen

    fly_energy_list = np.empty(len(power_dif)+1) #setting orignal energy in flywheel

    for i in range(len(power_dif)): #for each time step
        #the power in the flywheel starts at the power from the end
        #of the last time step
        #converted to energy (J) by multiplying by number of seconds in 5 minutes
        fly_energy = fly_energy_list[i] + power_dif[i]*300

        if fly_energy < 0: #if flywheel power is negative
            fly_energy = 0 #set flywheel power to zero
        elif fly_energy > max_fly: #if flywheel energy is higher than max
            fly_energy = max_fly #set flywheel power to maximum

        fly_energy_list[i+1] = fly_energy #setting the next fly_energy

    fly_energy_list = np.delete(fly_energy_list,0) #deleting the original 0

    power_array = np.where(power_dif<0, power_array+fly_energy_list/300,power_array)
    #chaning any power in the genrator that exceeds the maximum to the max
    power_array = np.where(power_array>max_gen,max_gen,power_array)
    #converting to enery (J)
    gen_energy = energy_function(power_array)
    return(gen_energy)

def all_flywheel_gen_energy(power_array,gen_min,gen_max,fly_min,fly_max,num_gen,num_fly):
    """calculates the amount of energy collected for every combination of flywheel and
    generator size between gen_min and gen_max and fly_min and fly_max
    Inputs:
    power_array: power of wind turbine facing in the optimal direction
    gen_min: max wind speed (m/s) the min generator could capture
    gen_max: max wind speed (m/s) the min generator could capture
    fly_min: ammount time (s) a 12 m/s wind would have to blow to fill max flywheel
    fly_max: amount time (s) a 12 m/s wind would have to blow to fill min flywheel
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between 7 and 12
    num_fly: number of different sizes a flywheel could be
    Outputs:
    gen_energy_array: array of the sums of energy collected by every
                      generator and flywheel combination
    """
    fly_max = fly_max*power_function(12) #converting to J
    fly_min = fly_min*power_function(12) #converting to J
    #creates an array with the dimensions of num_gen by num_fly
    #this array will contain the energy generated by every combo of generators and flywheels
    gen_energy_array = np.empty((num_gen,num_fly))
    for i in range(num_gen): #for each gen size
        for j in range(num_fly): #for each fly size
            #num gen is distributed between gen_min and gen_max
            #num fly is distributed between the power equivilents of fly_min and fly_max
            gen_energy_array[i,j] = flywheel_energy(power_array,power_function(gen_min+(i/(num_gen-1))*(gen_max-gen_min)),fly_min+(j/(num_fly-1)*fly_max))
    return gen_energy_array

def cost_curve(gen_size,fly_size,energy):
    """calculates the cost of a turbine in dollars per kilowatt assuming it
    runs for 20 years
    Inputs:
    gen_size: max wind speed (m/s) the generator could capture
    fly_size: ammount time (s) a 12 m/s wind would have to blow to fill flywheel
    energy: energy collected in J
    Outputs:
    cost: the cost of the turbine in dollars per kilowatt
    """
    #assuming a life span of 20 years and the generator and inverter are each replaced once
    gen_size = power_function(gen_size) #converting to Watts
    mech_cost = 1118 #one time mechanical cost
    invert_cost = .35 * gen_size *2 #cost of the interter REPLACED ONCE
    gen_cost = (-gen_size*.00036+.94)*gen_size #cost of the generator REPLACED ONCE
    fly_cost = (8.3**-5)*fly_size #cost of the flywheel
    kilowat_hour = energy/(60 * 60 * 1000) #converting J to kilowatt hour
    #summming all the costs, kilowat_hour is multiplied by the number of years
    cost = (mech_cost+invert_cost+gen_cost+fly_cost)/(20*kilowat_hour)
    return cost

def best_cost(gen_min,gen_max,fly_min,fly_max,num_gen,num_fly,energy):
    """calculates the lowest possible cost in dollars per kilowatt
    Inputs:
    gen_min: max wind speed (m/s) the min generator could capture
    gen_max: max wind speed (m/s) the min generator could capture
    fly_min: ammount time (s) a 12 m/s wind would have to blow to fill max flywheel
    fly_max: amount time (s) a 12 m/s wind would have to blow to fill min flywheel
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between 7 and 12
    num_fly: number of different sizes a flywheel could be
    energy: energy collected in J
    Outputs:
    low_cost: lowest cost in dollars per kilowatt hour
    low_gen: generator (m/s) that produced the lowest cost
    low_fly: flywheel (s) that produced the lowest cost
    """
    fly_max = fly_max*power_function(12) #convert to J
    fly_min = fly_min*power_function(12) #cnvert to J
    #creates an array with dimensions 3 by num gen by num_fly
    fly_gen_size_array = np.empty((3,num_gen,num_fly))

    for i in range(num_gen): #for each gen size
        #num gen is distributed between gen_min and gen_max
        gen_size = gen_min+(i/(num_gen-1))*(gen_max-gen_min)
        for j in range(num_fly): #for each fly size
            #num fly is distributed between the power equivilents of fly_min and fly_max
            fly_size = fly_min+(j/(num_fly-1)*fly_max)
            #calculates cost for this combo of gen size and fly size
            fly_gen_size_array[:,i,j] = cost_curve(gen_size,fly_size,energy[i,j]),gen_size,fly_size

    low_cost = np.amin(fly_gen_size_array[0]) #lowest cost in the array

    for i in range(num_gen): #for each gen size
        for j in range(num_fly): #for each fly size
            if fly_gen_size_array[0,i,j] == low_cost: #if the cost equals the lowest cosr
                low_gen = fly_gen_size_array[1,i,j] #set the gen size
                low_fly = fly_gen_size_array[2,i,j] #set the fly size
    return(low_cost,low_gen,low_fly)

def dump_pickles_one_gen(name,width,num_angles,gen_min,gen_max,best_percent,num_gen):
    """pickles generator sizes that capture optimal energy lists
    Inputs: name: string that was used to label the files when loading them
    width: width in radians that wind can be collected with no loss
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    gen_min: max wind speed the min generator could capture in m/s
    gen_max: max wind speed the min generator could capture in m/s
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between gen_min and gen_max m/s
    best_percent: the optimal percentage of energy for a genrator to collect
    """
    #redirecting to the file containing fiveMinutes data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/fiveMinutes10')
    #initilizing all the differnt lists of data
    #these are lists containing data point per coordinate
    x = []
    y = []
    gen_list = []
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
        info = coordinate_info(u10,v10,num_angles,width)
        power_array = info[1][0] #list of power every 5 minutes at the best angle
        best_energy = info[0][1] #sum of energy at the best angle
        energy = best_energy/num_years #divided by 3 so its annual
        gen = generator_classification(power_array,best_energy,gen_min,gen_max,num_gen,best_percent)[0]
        #adding the data point for this coordinate to the list containing
        gen_list.append(gen)
        y.append(coord[0]-25)
        x.append(coord[1]+125)

    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt', 'wb'))
    pickle.dump(y,open('y.txt', 'wb'))
    pickle.dump(gen_list,open('gen_list_%s.txt' % (name), 'wb'))

def dump_pickles_one_fly(name,width,num_angles,gen_size,fly_size):
    """pickles flywheel and generator annual energy lists
    Inputs: name: string that was used to label the files when loading them
    width: width in radians that wind can be collected with no loss
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    gen_max: max wind speed (m/s) the generator could capture
    fly_min: ammount time (s) a 12 m/s wind would have to blow to fill the flywheel
    """
    #redirecting to the file containing fiveMinutes data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/fiveMinutes10')
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
        info = coordinate_info(u10,v10,num_angles,width)
        power_array = info[1][0] #list of power every 5 minutes at the best angle
        flywheel_gen = flywheel_energy(power_array,power_function(gen_size),fly_size*power_function(12))
        flywheel_gen = flywheel_gen/num_years #divided by 3 to make it annual
        flywheel_gen_plain = generator_energy(power_array,gen_size)/num_years
        #adding the data point for this coordinate to the list containing

        flywheel_gen_list.append(flywheel_gen)
        flywheel_gen_plain_list.append(flywheel_gen_plain)
        y.append(coord[0]-25)
        x.append(coord[1]+125)

    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt', 'wb'))
    pickle.dump(y,open('y.txt', 'wb'))
    pickle.dump(flywheel_gen_list,open('flywheel_gen_list_%s.txt' % (name), 'wb'))
    pickle.dump(flywheel_gen_plain_list,open('flywheel_gen_plain_list_%s.txt' % (name), 'wb'))

def dump_pickles_cost(name,width,num_angles,gen_min,gen_max,fly_min,fly_max,num_fly,num_gen):
    """pickles lowest costs lists and their generator and flywheel sizes
    Inputs: name: string that was used to label the files when loading them
    width: width in radians that wind can be collected with no loss
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    gen_min: max wind speed (m/s) the min generator could capture
    gen_max: max wind speed (m/s) the min generator could capture
    fly_min: ammount time (s) a 12 m/s wind would have to blow to fill max flywheel
    fly_max: amount time (s) a 12 m/s wind would have to blow to fill min flywheel
    num_gen: number of different sizes a generator could be
             the sizes are equally distributed between 7 and 12
    num_fly: number of different sizes a flywheel could be
    """
    #redirecting to the file containing fiveMinutes data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/fiveMinutes10')
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
        info = coordinate_info(u10,v10,num_angles,width)
        power_array = info[1][0] #list of power every 5 minutes at the best angle
        all_flywheel = all_flywheel_gen_energy(power_array,gen_min,gen_max,fly_min,fly_max,num_gen,num_fly)
        low_cost,best_gen_size,best_fly_size = best_cost(gen_min,gen_max,fly_min,fly_max,num_gen,num_fly,all_flywheel)
        #adding the data point for this coordinate to the list containing
        low_cost_list.append(low_cost)
        best_gen_size_list.append(best_gen_size)
        best_fly_size_list.append(best_fly_size)
        y.append(coord[0]-25)
        x.append(coord[1]+125)

    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt', 'wb'))
    pickle.dump(y,open('y.txt', 'wb'))
    pickle.dump(low_cost_list,open('low_cost_list_%s.txt' % (name), 'wb'))
    pickle.dump(best_gen_size_list,open('best_gen_size_list_%s.txt' % (name), 'wb'))
    pickle.dump(best_fly_size_list,open('best_fly_size_list_%s.txt' % (name), 'wb'))

def dump_pickles_basic(name,width,num_angles):
    """pickles flywheel and generator annual energy lists
    Inputs: name: string that was used to label the files when loading them
    width: width in radians that wind can be collected with no loss
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    """
    #redirecting to the file containing fiveMinutes data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/fiveMinutes10')
    #initilizing all the differnt lists of data
    #these are lists containing data point per coordinate
    x = []
    y = []
    energy_list = []
    angle_list = []
    power_list = []
    speed_list = []
    velocity_list = []
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
        info = coordinate_info(u10,v10,num_angles,width)
        power_array = info[1][0] #list of power every 5 minutes at the best angle
        best_energy = info[0][1] #sum of energy at the best angle
        energy = best_energy/num_years #divided by 3 so its annual
        angle = info[0][0] #angle that collects the most energy
        power = np.sum(power_array)/len(power_array) #average power
        speed = np.sum(info[1][2])/len(info[1][2]) #average speed
        velocity = np.sum(info[1][1])/len(info[1][1]) #average velocity
        #adding the data point for this coordinate to the list containing
        energy_list.append(energy)
        angle_list.append(angle)
        power_list.append(power)
        speed_list.append(speed)
        velocity_list.append(velocity)
        y.append(coord[0]-25)
        x.append(coord[1]+125)

    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/data')
    #pickles data
    pickle.dump(x,open('x.txt', 'wb'))
    pickle.dump(y,open('y.txt', 'wb'))
    pickle.dump(energy_list,open('energy_list_%s.txt' % (name), 'wb'))
    pickle.dump(angle_list,open('angle_list_%s.txt' % (name), 'wb'))
    pickle.dump(power_list,open('power_list_%s.txt' % (name), 'wb'))
    pickle.dump(speed_list,open('speed_list_%s.txt' % (name), 'wb'))
    pickle.dump(velocity_list,open('velocity_list_%s.txt' % (name), 'wb'))


dump_pickles_cost('test',math.pi,16,6,12,300,1800,6,6)
