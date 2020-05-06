from matplotlib import pyplot as plt
from dump import *
from calc import *
from load import *

def add_axis():
    """adds the values of longitude and latitiude coordinates along the x and y axis
    """
    plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 10) #adds x axis
    plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 10) #adds y axis

def add_all(title):
    """adds the title and labels x and y axis and longitude and latitude
    Inputs: title: a string of the title of the graph
    """
    add_axis()
    plt.xlabel('Longitude', fontsize = 10) #labels x axis as longitude
    plt.ylabel('Latitude', fontsize = 10) #labels y axis as latitude
    plt.title(title, fontsize = 20)

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
    #plt.clim(8.75, 10.25); #sets color bar value limits
    plt.clim(7, 11)
    plt.show() #displays graph

def power_graph(power_list,x,y):
    """graphs average power a wind turbine could collect from the wind
    the wind turbine can collect wind from a given range of angles
    Inputs: energy_list: list of average power (W) at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = power_list,label = 'Weather Site',cmap ='PuBu_r') #creates scatterplot
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
    plt.clim(0,1); #sets color bar value limits
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

def cost_graph(cost_list,x,y):
    """graphs the dollar per kilowatt cost at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: cost_list: list of dollar per kilowatt cost at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c =
    cost_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Dollar per kilowatt Hour')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Dollar per kilowatt Hour', fontsize = 20) #adds color bar label
    plt.clim(0,.4); #sets color bar value limits
    plt.show() #displays graph

def cost_cutoff_graph(cost_list,cutoff,x,y):
    """graphs the low cost areas
    Inputs: cost_list: list of dollar per kilowatt cost at each weather site
            cutoff: minimum low cost
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    new_cost = np.where(cost_list<=cutoff,cost_list,.4)
    plt.scatter(x,y,c = new_cost,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('High and Low Cost Areas')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
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

def capacity_graph(gen_energy_list,gen_size,x,y):
    """graphs the percwntage of max energy output at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: gen_energy_list: how much energy generator collected in watts
            gen_size: size in KW of gen
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = (gen_energy_list/3600000)/(8760*gen_size),label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Percentage of Maximum Energy Output')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Capacity', fontsize = 20) #adds color bar label
    plt.clim(0,.5); #sets color bar value limits
    plt.show() #displays graph

def solar_graph(gen_energy_list,x,y):
    """graphs the percentage energy generated compared to how much
    solar energy could be peoducedat each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: gen_energy_list: how much energy generator collected in watts
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    #37 is number of turbines
    plt.scatter(x,y,c = ((gen_energy_list/3600000)*37)/1108687.5,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Solar Percentage')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Percentage of Solar KWH', fontsize = 20) #adds color bar label
    plt.clim(0,.5); #sets color bar value limits
    plt.show() #displays graph

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

def load_graphs_cost(name):
    """graphs lowest cost (in dollar per kilowatt hour), and their respective flywheel
    and generator sizes
    Inputs: name: string that was used to label the files when loading them
    """
    x,y,low_cost_list, best_gen_size_list,best_fly_size_list = load_pickles_cost(name)
    cost_graph(low_cost_list,x,y) #graphs lowest dollar per kilowatt cost
    best_gen_size_graph(best_gen_size_list,x,y) #graphs generator size with lowest cost
    best_fly_size_graph(best_fly_size_list,x,y) #graphs flywheel size with lowest cost

def load_graphs_basic(name):
    """graphs several basic info graphs (energy,power,speed,velocity,velocity/speed,angle)
    Inputs: name: string that was used to label the files when loading them
    """
    x,y,energy_list,angle_list,power_list,speed_list,velocity_list,gen_energy_list,cost_list = load_pickles_basic(name)
    energy_graph(energy_list,x,y) #graphs annual energy of a turbine
    power_graph(power_list,x,y) #graphs average power collected by a turbine
    speed_graph(speed_list,x,y) #graphs average speed of wind
    velocity_graph(velocity_list,x,y) #graphs average velocity of wind collected by a turbine
    speed_proportion_graph(velocity_list, speed_list,x,y) #graphs velocit divided by speed
    angle_graph(angle_list,x,y) #graphs vectors that represent the angle that collects the highest annual energy

def load_graphs_capacity(name,gen_size,cutoff=False):
    """graphs several capacity and cost graphs
    Inputs: name: string that was used to label the files when loading them
            gen_size: size in KW of gen
    """
    x,y,energy_list,angle_list,power_list,speed_list,velocity_list,gen_energy_list,cost_list,velocity2_list = load_pickles_basic(name)
    cost_graph(cost_list,x,y)
    capacity_graph(gen_energy_list,gen_size,x,y)
    solar_graph(gen_energy_list,x,y)
    if cutoff:
        cost_cutoff_graph(cost_list,cutoff,x,y)

if __name__ == '__main__':
    load_graphs_capacity('power',5)
