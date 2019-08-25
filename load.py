import numpy as np
import math as math
import pickle
import glob
import os
from matplotlib import pyplot as plt

ro=1.225 #kg/m3 density of air
cp = .35 #coefficient of performance
radius = 1 #radius in meters
area = math.pi*(radius**2) #area in meters squared
num_years = 3

def power_function(speed_array):
    """calculates power
    Input: wind speed m/s
    Output: power in Watts"""
    power_array= .5*ro*cp*area*(np.power(speed_array,3))
    return power_array

def load_pickles_one_gen(name):
    """loads generator sizes that capture optimal energy lists that have been pickled
    Inputs: name: string that was used to label the files when loading them
    """
    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/data')
    #loads data
    x = pickle.load(open('x.txt', 'rb'))
    y = pickle.load(open('y.txt', 'rb'))
    gen_list = pickle.load(open('gen_list_%s.txt' % (name), 'rb'))
    return (x,y,gen_list)

def load_pickles_one_fly(name):
    """loads flywheel and generator annual energy lists that have been pickled
    Inputs: name: string that was used to label the files when loading them
    """
    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/data')
    #loads data
    x = pickle.load(open('x.txt', 'rb'))
    y = pickle.load(open('y.txt', 'rb'))
    flywheel_gen_list = pickle.load(open('flywheel_gen_list_%s.txt' % (name), 'rb'))
    flywheel_gen_plain_list = pickle.load(open('flywheel_gen_plain_list_%s.txt' % (name), 'rb'))
    return (x,y,flywheel_gen_list,flywheel_gen_plain_list)

def load_pickles_cost(name):
    """loads lowest costs lists and their generator and flywheel sizes that have been pickled
    Inputs: name: string that was used to label the files when loading them
    """
    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/data')
    #loads data
    x = pickle.load(open('x.txt', 'rb'))
    y = pickle.load(open('y.txt', 'rb'))
    low_cost_list = pickle.load(open('low_cost_list_%s.txt' % (name), 'rb'))
    best_gen_size_list = pickle.load(open('best_gen_size_list_%s.txt' % (name), 'rb'))
    best_fly_size_list = pickle.load(open('best_fly_size_list_%s.txt' % (name), 'rb'))
    print(best_gen_size_list)
    print(best_fly_size_list)
    return (x,y,low_cost_list,best_gen_size_list,best_fly_size_list)

def load_pickles_basic(name):
    """loads energy, angle, power, speed, and velocity lists that have been pickled
    Inputs: name: string that was used to label the files when loading them
    """
    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/data')
    #loads data
    x = pickle.load(open('x.txt', 'rb'))
    y = pickle.load(open('y.txt', 'rb'))
    energy_list = np.array(pickle.load(open('energy_list_%s.txt' % (name), 'rb')))
    angle_list = np.array(pickle.load(open('angle_list_%s.txt' % (name), 'rb')))
    power_list = np.array(pickle.load(open('power_list_%s.txt' % (name), 'rb')))
    speed_list = np.array(pickle.load(open('speed_list_%s.txt' % (name), 'rb')))
    velocity_list = np.array(pickle.load(open('velocity_list_%s.txt' % (name), 'rb')))
    return (x,y,energy_list,angle_list,power_list,speed_list,velocity_list)

def load_graphs_cost(name):
    """graphs lowest cost (in dollar per kilowatt hour), and their respective flywheel
    and generator sizes
    Inputs: name: string that was used to label the files when loading them
    """
    x,y,low_cost_list, best_gen_size_list,best_fly_size_list = load_pickles_cost(name)
    low_cost_graph(low_cost_list,x,y) #graphs lowest dollar per kilowatt cost
    best_gen_size_graph(best_gen_size_list,x,y) #graphs generator size with lowest cost
    best_fly_size_graph(best_fly_size_list,x,y) #graphs flywheel size with lowest cost

def load_graphs_basic(name):
    """graphs several basic info graphs (energy,power,speed,velocity,velocity/speed,angle)
    Inputs: name: string that was used to label the files when loading them
    """
    x,y,energy_list,angle_list,power_list,speed_list,velocity_list = load_pickles_basic(name)
    energy_graph(energy_list,x,y) #graphs annual energy of a turbine
    power_graph(power_list,x,y) #graphs average power collected by a turbine
    speed_graph(speed_list,x,y) #graphs average speed of wind
    velocity_graph(velocity_list,x,y) #graphs average velocity of wind collected by a turbine
    speed_proportion_graph(velocity_list, speed_list,x,y) #graphs velocit divided by speed
    angle_graph(angle_list,x,y) #graphs vectors that represent the angle that collects the highest annual energy

def add_axis():
    """adds the values of longitude and latitiude coordinates along the x and y axis
    """
    plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15) #adds x axis
    plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15) #adds y axis

def add_all(title):
    """adds the title and labels x and y axis and longitude and latitude
    Inputs: title: a string of the title of the graph
    """
    add_axis()
    plt.xlabel('Longitude', fontsize = 20) #labels x axis as longitude
    plt.ylabel('Latitude', fontsize = 20) #labels y axis as latitude
    plt.title(title, fontsize = 25)

def load_graphs_one_fly(name):
    """graphs annuall energy when a generator of a specific size has no flywheel
    vs when the same generator has a fywheel of a specific size
    the wind turbine can collect wind from a given range of angles
    Inputs: name: string that was used to label the files when loading them
    """
    x,y,flywheel_gen_list,flywheel_gen_plain_list = load_pickles_one_fly(name)
    plt.figure(figsize = (5,20)) #sets size of the graph

    #GENERATOR WITH FLYHWEEL ENERGY
    plt.subplot(2,1,1) #switches to the second subplot
    plt.scatter(x,y,c = np.log10(flywheel_gen_list),label = 'Weather Site',cmap ='jet') #creates scatterplot
    plt.title('Annual Energy Stored in Generator with Flywheel', fontsize = 15) #adds title
    plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15) #adds y axis
    plt.xticks(fontsize = 0) #adds x axis
    plt.ylabel('Latitude', fontsize = 20) #labels y axis as latitude
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Log10 of Average Annual Energy (J)', fontsize = 20) #adds color bar label
    plt.clim(8.5, 9.5); #sets color bar value limits

    #GENERATOR WITHOUT FLYWHEEL ENERGY
    plt.subplot(2,1,2) #switches to the third subplot
    plt.scatter(x,y,c = np.log10(flywheel_gen_plain_list),label = 'Weather Site',cmap ='jet') #creates scatterplot
    plt.title('Annual Energy Stored in Generator Without Flywheel', fontsize = 15) #adds title
    add_axis() #adds x and y axis numbers and ticks
    plt.xlabel('Longitude', fontsize = 20) #labels x axis as longitude
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    plt.clim(8.5, 9.5); #sets color bar value limits
    plt.show() #displays graph

def load_graphs_one_gen(name):
    """graphs the optimal generator size that collects closest to a given optimal
    percentage of annual energy
    the wind turbine can collect wind from a given range of angles
    Inputs: name: string that was used to label the files when loading them
    """
    x,y,gen_list = load_pickles_one_gen(name)
    plt.scatter(x,y,c = gen_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Generator Size that Collects 80 Percent of Energy')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Generator Size (m/s)', fontsize = 20) #adds color bar label
    plt.clim(min(gen_list), max(gen_list)); #sets color bar value limits
    plt.show() #displays graph

def energy_graph(energy_list,x,y):
    """graphs annuall energy when a generator has no maximum size
    the wind turbine can collect wind from a given range of angles
    Inputs: energy_list: list of annual energy (J) at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = np.log10(energy_list),label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Annual Energy')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Log10 of Average Annual Energy (J)', fontsize = 20) #adds color bar label
    plt.clim(8.75, 10.25); #sets color bar value limits
    plt.show() #displays graph

def power_graph(power_list,x,y):
    """graphs average power a wind turbine could collect from the wind
    the wind turbine can collect wind from a given range of angles
    Inputs: energy_list: list of average power (W) at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = power_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Average Power')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Power (W)', fontsize = 20) #adds color bar label
    plt.clim(20, 150); #sets color bar value limits
    plt.show() #displays graph

def speed_graph(speed_list,x,y):
    """graphs average speed of the wind at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: speed_list: list of average speed (m/s) at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = speed_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Average Wind Speed')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Speed (m/s)', fontsize = 20) #adds color bar label
    plt.clim(1, 7); #sets color bar value limits
    plt.show() #displays graph

def velocity_graph(velocity_list,x,y):
    """graphs average velocity of the wind at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: velocity_list: list of average velocity (m/s) at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = velocity_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Average WInd Velocity')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Velocity (m/s)', fontsize = 20) #adds color bar label
    plt.clim(1, 7); #sets color bar value limits
    plt.show() #displays graph

def speed_proportion_graph(velocity_list, speed_list,x,y):
    """graphs average velocity divided by average speed of the wind at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: velocity_list: list of average velocity (m/s) at each weather site
            speed_list: list of average speed (m/s) at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = velocity_list/speed_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Average Velocity/Average Speed')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color ba
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    plt.clim(.5,1); #sets color bar value limits
    plt.show() #displays graph

def angle_graph(angle_list,x,y):
    """graphs angle of wind that produces the most annual energy at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: angle_list: list of which angle of wind turbine collects the most annual energy
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    u_array = np.sin(angle_list) #north/south
    v_array = np.cos(angle_list) #east/west
    plt.quiver(x,y, u_array, v_array) #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Wind Angle')
    plt.show() #displays graph

def low_cost_graph(low_cost_list,x,y):
    """graphs the minimum dollar per kilowatt cost at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: low_cost_list: list of minimum dollar per kilowatt cost at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = low_cost_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Optimal Dollar per kilowatt Hour')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Dollar per kilowatt Hour', fontsize = 20) #adds color bar label
    plt.clim(0,.2); #sets color bar value limits
    plt.show() #displays graph

def best_gen_size_graph(best_gen_size_list,x,y):
    """graphs the generator size with the minumum dollar per kilowatt cost at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: best_gen_size_list: list of generator sizes with the minimum dollar per
                                kilowatt cost at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    print('start')
    print(best_gen_size_list)
    plt.scatter(x,y,c = best_gen_size_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    print('scatter')
    #adds x and y axis ticks and labels, and the title
    add_all('Optimal Generator Size')
    print('labels')
    plt.legend(loc=3, fontsize = 15) #adds legend
    print('colorbar')
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Generator Size (m/s)', fontsize = 20) #adds color bar label
    print('hello')
    plt.clim(min(best_gen_size_list),min(best_gen_size_list)); #sets color bar value limits
    print('almost done')
    plt.show() #displays graph

def best_fly_size_graph(best_fly_size_list,x,y):
    """graphs the flywheel size with the minumum dollar per kilowatt cost at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: best_gen_size_list: list of flywheel sizes with the minimum dollar per
                                kilowatt cost at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = best_fly_size_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Optimal Flywheel Size')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Flywheel Size (J)', fontsize = 20) #adds color bar label
    plt.clim(min(best_fly_size_list),max(best_fly_size_list)); #sets color bar value limits
    plt.show() #displays graph

def power_average(name,bucket_size,max_power):
    """prints the frequency that each average power falls within a range the size of bucket_size
       also graphs the distribution of average powers
    Inputs: name: string that was used to label the files when loading them
            bucket_size: range in Watts of average power that will be bucketed together
            max_power: max wind speed (m/s) the min generator could capture
    """
    #loading all lists stored in load_pickles_basic
    (x,y,energy_list,angle_list,power_list,speed_list,velocity_list) = load_pickles_basic(name)
    max_power = power_function(max_power) #converting from m/s to Watts
    #creating a list that will hold the percentage of wind that falls within each range of average power
    percent_list = []
    #calculating the number of different buckets there will have to be
    num_buckets = math.ceil(max_power/bucket_size)
    for i in range(num_buckets): #for each bucket
        percent_list.append(0) #each bucket starts with 0 percent
        for power in power_list: #for each coordinates average power
            #if an average power is within the range of the current bucket
            if power > i*bucket_size and power < (i+1)*bucket_size:
                #adds a count to the percentage list
                percent_list[i] += 1

    #converting to percent by dividing by number of coordinates and multiplying by 100
    percent_list = percent_list*100/len(power_list)

    for i in range(num_buckets): #for each bucket
        if percent_list[i] != 0: #if the percent is not 0
            #prints the percetnage of weather sites whose average power fall within the cuttent bucket
            print(percent_list[i],'percent of weather sites between',i*bucket_size,'Watts and',(i+1)*bucket_size, 'Watts \n')

    ##AVERAGE POWER DISTRUBUTION HISTOGRAM
    plt.hist(power_list, bins = num_buckets,range = (0,max_power)) #creates histogram
    plt.title('Frequency of Power at Different Coordinates', fontsize = 25) #adds title
    plt.xlabel('Average Power (Watts)', fontsize = 20) #labels x axis as longitude
    plt.ylabel('Number of Locations', fontsize = 20) #labels y axis as latitude
    plt.xticks(fontsize = 15) #setting font size of x axis values
    plt.yticks(fontsize = 15) #setting font size of y axis values
    plt.show() #displays graph

def one_coord_info(name,coord):
    """prints average wind speed, average wind velocity, average power
    and annual energy nof a given coordinate
    Inputs: name: string that was used to label the files when loading them
            coord: coordinate (latitude, longitude) ranging from -90 to 90 and -180 to 180 respectivly
     """
    #loading all lists stored in load_pickles_basic
    (x,y,energy_list,angle_list,power_list,speed_list,velocity_list) = load_pickles_basic(name)
    #creates a list that will contain each coordinates distance from the given coord
    distance = []
    coord_y = coord[0]-25 #converting to latitude
    coord_x = coord[1]+125 #converting to longitude
    for i in range (len(x)): #for each coordinate value
        #distance (in corrdinates) between a coordinate and the given coordinate in y direction
        lat_dist = y[i]-coord_y
        #distance (in corrdinates) between a coordinate and the given coordinate in x direction
        long_dist = x[i]-coord_x
        #total distance (in coordinates) between a coordinate and the given coordinate
        total_dist = math.sqrt(long_dist**2 + lat_dist**2)
        distance.append(total_dist) #adding total distance to distance list

    coord_index = distance.index(min(distance)) #finds the index of the smallest distance
    #prints info about the coordinate closets to the given coordinate
    print('closest site to', coord,'is',(y[coord_index]+25,x[coord_index]-125),
          '\naverage wind speed is', speed_list[coord_index],
          '\naverage wind velocity is', velocity_list[coord_index],
          '\naverage power is', power_list[coord_index],
          '\nannual energy is', energy_list[coord_index])


#load_graphs_cost('test')
load_pickles_cost('test')







def cost_curve(gen_size,fly_size,energy):
    #assuming a life span of 20 years
    gen_size = power_function(gen_size)
    mech_cost = 1118
    invert_cost = .35 * gen_size *2 #replaced once
    gen_cost = (-gen_size*.00036+.94)*gen_size #replaced once
    #print(gen_cost)
    #print('fly size', fly_size)
    fly_cost = (8.3**-5)*fly_size
    #print(fly_cost)
    kilowat_hour = energy/(60 * 60 * 1000) #converting J to kilowatt hour
    #print(kilowat_hour*20)
    dollar_per_watt = (mech_cost+invert_cost+gen_cost+fly_cost)/(20*kilowat_hour)
    return dollar_per_watt

def best_cost(num_gen,num_fly,energy):
    max_fly = 1800*power_function(12)
    min_fly = 300*power_function(12)

    fly_gen_size_array = np.empty((3,num_gen,num_fly))

    for i in range(num_gen):
        gen_size = 6+(i/(num_gen-1))*6
        for j in range(num_fly):
            fly_size = min_fly+(j/(num_fly-1)*max_fly)
            fly_gen_size_array[:,i,j] = cost_curve(gen_size,fly_size,energy[i,j]),gen_size,fly_size

    low_cost = np.amin(fly_gen_size_array[0])

    for i in range(num_gen):
        for j in range(num_fly):
            if fly_gen_size_array[0,i,j] == low_cost:
                low_gen = fly_gen_size_array[1,i,j]
                low_fly = fly_gen_size_array[2,i,j]
    return(low_cost,low_gen,low_fly)

def all_coords_best_cost(all_flywheel_list):
    all_flywheel_list = np.array(all_flywheel_list)
    num_gen = len(all_flywheel_list[0,:,0])
    num_fly = len(all_flywheel_list[0,0,:])

    best_cost_list = []
    best_gen_size_list = []
    best_fly_size_list = []

    for energy in all_flywheel_list:
        best_cost_list.append(best_cost(num_gen,num_fly,energy)[0])
        best_gen_size_list.append(best_cost(num_gen,num_fly,energy)[1])
        best_fly_size_list.append(best_cost(num_gen,num_fly,energy)[2])

    return best_cost_list,best_gen_size_list,best_fly_size_list

os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/data')
all_flywheel_list = pickle.load(open('all_flywheel_list_%s.txt' % ('60_min_fly'), 'rb'))
x = pickle.load(open('x.txt', 'rb'))
y = pickle.load(open('y.txt', 'rb'))
#(x,y,all_flywheel_list) = load_pickles_cost('30_min_fly')

best_cost_list,best_gen_size_list,best_fly_size_list = all_coords_best_cost(all_flywheel_list)

###COST
plt.scatter(x,y,c = best_cost_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
add_all('Optimal Dollar per Kilowatt Hour')
plt.legend(loc=3, fontsize = 15) #adds legend
cbar = plt.colorbar(cmap = 'jet') #creates color bar
cbar.ax.tick_params(labelsize=15)
cbar.set_label(label = 'Dollar per kilowatt Hour', fontsize = 20) #adds color bar label
plt.clim(0,.2); #sets color bar value limits
plt.show() #displays graph

####BEST GEN SIZE
plt.scatter(x,y,c = best_gen_size_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
add_all('Optimal Generator Size')
plt.legend(loc=3, fontsize = 15) #adds legend
cbar = plt.colorbar(cmap = 'jet') #creates color bar
cbar.ax.tick_params(labelsize=15)
cbar.set_label(label = 'Generator Size (m/s)', fontsize = 20) #adds color bar label
plt.clim(6,12); #sets color bar value limits
plt.show() #displays graph

plt.scatter(x,y,c = best_fly_size_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
add_all('Optimal Flywheel Size')
plt.legend(loc=3, fontsize = 15) #adds legend
cbar = plt.colorbar(cmap = 'jet') #creates color bar
cbar.ax.tick_params(labelsize=15)
cbar.set_label(label = 'Flywheel Size (J)', fontsize = 20) #adds color bar label
plt.clim(min(best_fly_size_list),max(best_fly_size_list)); #sets color bar value limits
plt.show() #displays graph
