import numpy as np
import math as math
from scipy.integrate import simps

from matplotlib import pyplot as plt

ro=1.225 #kg/m3 density of air
cp = .45 #coefficient of performance
# radius = 1 #radius in meters
# area = math.pi*(radius**2) #area in meters squared
area = 8
num_years = 3 #number of years data has been collected

def get_data(folder,file_name):
    """reads memory mapped file saves wind speed and direction from it
    Inputs: file_name: the name of the file
    Outputs: u_array: array wind speed (m/s) in north to south direction taken every 5 minutes
    v_array: array wind speed (m/s) in east to west direction taken every 5 minutes
    direction: array of wind direction (radians) taken every 5 minutes
               zero radians is the wind blowing exactly west
    """
    data = np.memmap(folder+file_name,mode='r+',dtype='float32',shape=(315360,2))
    data.flush()
    speed = np.array(data[:,0])
    direction = np.array(data[:,1])
    direction = 2*math.pi*direction/360 #converting to radians
    u_array = speed*np.sin(direction) #north/south
    v_array = speed*np.cos(direction) #east/west
    return u_array, v_array, direction

def speed_function(u_array,v_array,speed_up = 1):
    """calculates speed
    Input: wind vectors in the u and v directions in m/s
    speed_up: multiplied by the velocity (can be increased to mimic rooftop speeds)
    Output: wind speed in m/s"""
    speed_array = np.sqrt((u_array**2)+(v_array**2))*speed_up
    return speed_array

def power_function(speed_array):
    """calculates power
    Input: wind speed m/s
    Output: power in Watts"""
    x = speed_array

    #experimental cp, not currently in use
    a = .408784772
    b = -.0335235483
    c = -1.22127219
    d =  .00103098238
    e = -.0000104298924
    cp2 = a * x + b * (x**2) + c + d * (x**3) + e * (x**4)

    power_array = .5*ro*cp*area*(np.power(speed_array,3))
    return power_array

def reverse_power_function(power):
    """calculates speed based on power
    Input: power in Watts
    Output: wind speed in m/s"""
    speed = (np.power(power/(.5*ro*cp*area),1/3))
    return speed

def energy_function(power_array):
    """calculates energy
    Input: power in Watts
    Output: energy in J"""
    #creating the x coordinates that coorespond with each power value
    x = 5*np.arange(0,314860) #314860 data points each 5 minutes apart
    #converting to energy, 60 is converting from minutes to seconds
    energy = np.array(simps(power_array,x))*60
    return energy

def velocity_function(u_array,v_array,angle,width,perp=False,speed_up = 1):
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
    speed_array: speed of wind (m/s)
    speed_up multiplied by the velocity (can be increased to mimic rooftop speeds)
    perp: True when the turbine can only collect direct wind
          False when the turbine can collect all wind in width
    """

    speed_array = speed_function(u_array,v_array,speed_up)
    #angle in radians that the wind is blowing towards
    wind_angle = np.arctan2(u_array,v_array)+math.pi #making scale from 0 to 2pi
    #difference between wind direction and the angle the turbine is facing
    angle_difference = abs(wind_angle - angle)
    #no loss of speed if angle difference is within specified width
    #the lower the angle difference the more power the wind generates

    if perp == False:
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

def all_angle_power(u_array,v_array,num_angles,width,perp=False,speed_up=1):
    """calculates the power a turbine will collect when facing num_angles different
    directions and can collect wind without loss over a range of width radians
    Inputs:
    u_array and v_array: wind vectors in the u and v directions in m/s
    num_angles: number of different angles the wind turbine could be facing
                (equally distributed around a 2 pi radian circle)
    width: width in radians that wind can be collected with no loss
    Outputs: power of turbine facing num_angles different directions
    vel_factor: multiplied by the velocity (can be increased to mimic rooftop speeds)
    perp: True when the turbine can only collect direct wind
          False when the turbine can collect all wind in width
    """
    power_angle_list = [] #creates a list that will contain power at each angle
    for i in range(num_angles): #for each angle
        #calculates power of turbine
        power_angle_list.append(velocity_function(u_array,v_array,2*math.pi*(i/num_angles),width,perp,speed_up)[0])
        # power_angle_list.append(velocity_function(u_array,v_array,2*math.pi*(i/num_angles)-(math.pi/2),width,speed_up)[0])
    return np.array(power_angle_list)

def best_angle_energy(u_array,v_array,num_angles,width,speed_up = 1):
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
    power_all_angles = all_angle_power(u_array,v_array,num_angles,width,speed_up)
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

def coordinate_info(u_array,v_array,num_angles,width,perp=False,speed_up = 1):
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
    angles = best_angle_energy(u_array,v_array,num_angles,width,speed_up)
    wind_info = velocity_function(u_array,v_array,angles[0],width,perp,speed_up)
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


def all_generators_energy(power_array,original_energy,gen_min,gen_max,num_gen,fly_size):
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
        gen_energy = flywheel_energy(power_array,power_function(gen_min+(i/(num_gen-1))*(gen_max-gen_min)),fly_size)
        #percentage of original energy this generator collects
        # energy_difference = gen_energy/original_energy
        energy_difference = gen_energy/generator_energy(power_array,reverse_power_function(5000))
        energy_percents.append(energy_difference)
    #percentage difference between original energy and energy with all diferent generators
    return np.array(energy_percents)

def generator_classification(power_array,original_energy,gen_min,gen_max,num_gen,best_percent,fly_size):
    """classifying each weather location to an optimum generator size that collects the closest
    best_percent of the possible energy at that weather site
    Inputs:
    power_array: power ofnp_array wind turbine facing in the optimal direction in Watts
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
    percent_all_gen = all_generators_energy(power_array,original_energy,gen_min,gen_max,num_gen,fly_size)
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
            #adding the lowest percentage-
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
    if max_fly == 0:
        return generator_energy(power_array,reverse_power_function(max_gen))

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
                      gennp_arrayerator and flywheel combination
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

def cost_curve(gen_size,fly_size,energy,lifetime = 30):
    """calculates the cost of a turbine in dollars per kilowatt assuming it
    runs for 20 years
    Inputs:
    gen_size: max wind speed (m/s) the generator could capture
    fly_size: ammount time (s) a 12 m/s wind would have to blow to fill flywheel
    energy: energy collected in J
    lifetime: expected lifetime of a turbine
    Outputs:
    cost: the cost of the turbine in dollars per kilowatt
    """
    kilowatt_hours = energy/3600000
    gen_size = power_function(gen_size)/1000 #converting to kilowatts
    #8760 is number of hours in a year
    capacity = kilowatt_hours/(8760*gen_size)

    capital_cost = 2250*gen_size #TODO ADD COST CURVE

    capital_cost = (-1.04622719 * gen_size + 0.0665693 * (gen_size**2) + 5.93691848)*gen_size*1000

    maintenance = 44*gen_size #yearly maintenance cost          multiplied by lifetime?
    capital_recovery = (.03*(1+.03)**lifetime)/(((1+.03)**lifetime)-1)

    cost = (((capital_cost+maintenance)*.03)/(1-(1+.03)**(-lifetime)))/(gen_size*8760*capacity) #NREL

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

if __name__ == '__main__':
    pass
