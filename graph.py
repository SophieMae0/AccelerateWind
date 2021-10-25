from matplotlib import pyplot as plt
import matplotlib as mpl
from dump import *
from calc import *
from load import *


def add_all(title):
    """adds the title and labels x and y axis and longitude and latitude
    Inputs: title: a string of the title of the graph
    """
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
    plt.set_cmap('jet')
    cbar = plt.colorbar() #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Power (W)', fontsize = 20) #adds color bar label
    plt.clim(20, 500); #sets color bar value limits
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
    plt.clim(4, 5); #sets color bar value limits
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
    add_all('Average Wind Velocity')
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
    plt.scatter(x,y,c = velocity_list/speed_list,label = 'Weather Site',cmap ='jet', s = 5) #creates scatterplot
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
    plt.clim(0,.3); #sets color bar value limits
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
    plt.scatter(x,y,c = best_gen_size_list,label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Optimal Generator Size')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Generator Size (KW)', fontsize = 20) #adds color bar label
    plt.clim(2,5); #sets color bar value limits
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

def power_proportion_graph(power_list, potential_power_list,x,y):
    """graphs what percentage of potential power is being captured by turbine
    the wind turbine can collect wind from a given range of angles
    Inputs: velocity_list: list of average velocity (m/s) at each weather site
            speed_list: list of average speed (m/s) at each weather site
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    plt.scatter(x,y,c = power_list/potential_power_list,label = 'Weather Site',cmap ='jet', s = 5) #creates scatterplot

    #adds x and y axis ticks and labels, and the title
    add_all('Actual Power/Potential Power')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color ba
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    plt.clim(0,1); #sets color bar value limits
    plt.show() #displays graph

def solar_graph(gen_energy_list,capacity_list,x,y):
    """graphs the percentage energy generated compared to how much
    solar energy could be produced at each weather site
    the wind turbine can collect wind from a given range of angles
    Inputs: gen_energy_list: how much energy generator collected in watts
            x: list of x coordinates from 0 to 60
            y: list of y coordinates from 0 to 25
    """
    #37 is number of turbines
    # plt.scatter(x,y,c = capacity_list,label = 'Weather Site',cmap ='jet') 31536000
    plt.scatter(x,y,c = ((gen_energy_list/3600000)*37)/(capacity_list*(60*60*24*365*350*2812.5/3600000)),label = 'Weather Site',cmap ='jet') #creates scatterplot
    #adds x and y axis ticks and labels, and the title
    add_all('Solar Percentage')
    plt.legend(loc=3, fontsize = 15) #adds legend
    cbar = plt.colorbar(cmap = 'jet') #creates color bar
    cbar.ax.tick_params(labelsize=15) #sets colorbar fontsize
    cbar.set_label(label = 'Percentage of Solar KWH', fontsize = 20) #adds color bar label
    plt.clim(.0,.5); #sets color bar value limits
    plt.show() #displays graph

def load_graphs_capacity(name,solar_name,gen_size,cutoff=False):
    """graphs cost and solar capacity
    Inputs: name: string that was used to label the files when loading them
    solar_name: name of the solar data files
    gen_size: size of generator in KW
    cut_off: cutoff of cost graph
    """
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    x_solar = pickle.load(open('x%s.txt' % (solar_name), 'rb'))
    y_solar = pickle.load(open('y%s.txt' % (solar_name), 'rb'))
    capacity_list = pickle.load(open('capacity_list_%s.txt' % (solar_name), 'rb'))

    x,y,energy_list,angle_list,power_list,potential_power_list,speed_list,velocity_list,gen_energy_list,cost_list,state = load_pickles_basic(name) = load_pickles_basic(name)

    ordered_cap = []

    for i in range(len(x)):
        for j in range(len(x_solar)):
            if x[i] == x_solar[j]:
                if y[i] == y_solar[j]:
                    ordered_cap.append(capacity_list[j])

    cost_graph(cost_list,x,y)
    capacity_graph(gen_energy_list,gen_size,x,y)
    solar_graph(gen_energy_list,np.array(ordered_cap),x,y)
    if cutoff:
        cost_cutoff_graph(cost_list,cutoff,x,y)

def load_graphs_basic(name):
    """graphs several basic info graphs (energy,power,speed,velocity,velocity/speed,angle)
    Inputs: name: string that was used to label the files when loading them
    """
    x,y,energy_list,angle_list,power_list,potential_power_list,speed_list,velocity_list,gen_energy_list,cost_list,state = load_pickles_basic(name) = load_pickles_basic(name)

    energy_graph(energy_list,x,y) #graphs annual energy of a turbine
    power_graph(power_list,x,y) #graphs average power collected by a turbine
    speed_graph(speed_list,x,y) #graphs average speed of wind
    velocity_graph(velocity_list,x,y) #graphs average velocity of wind collected by a turbine
    speed_proportion_graph(velocity_list, speed_list,x,y) #graphs velocity divided by speed
    power_proportion_graph(power_list, potential_power_list,x,y) #graphs power divided by total possible power proportion

def load_graphs_state_basic(nsmae,state_name):
    x,y,energy_list,angle_list,power_list,potential_power_list,speed_list,velocity_list,gen_energy_list,cost_list,state = load_pickles_basic(name)

    #converts the list of stings into lists of floats
    x = np.asarray(x, dtype=np.float64, order='C')
    y = np.asarray(y, dtype=np.float64, order='C')
    energy_list = np.asarray(energy_list, dtype=np.float64, order='C')
    angle_list = np.asarray(angle_list, dtype=np.float64, order='C')
    power_list = np.asarray(power_list, dtype=np.float64, order='C')
    potential_power_list = np.asarray(potential_power_list, dtype=np.float64, order='C')
    speed_list = np.asarray(speed_list, dtype=np.float64, order='C')
    velocity_list = np.asarray(velocity_list, dtype=np.float64, order='C')
    gen_energy_list = np.asarray(gen_energy_list, dtype=np.float64, order='C')
    cost_list = np.asarray(cost_list, dtype=np.float64, order='C')

    #returns only the coordinates within the specified state
    mask = np.where(state==state_name,False,True)
    x = np.delete(x,mask)
    y = np.delete(y,mask)
    energy_list = np.delete(energy_list,mask)
    angle_list = np.delete(angle_list,mask)
    power_list = np.delete(power_list,mask)
    potential_power_list = np.delete(potential_power_list,mask)
    speed_list = np.delete(speed_list,mask)
    velocity_list = np.delete(velocity_list,mask)
    gen_energy_list = np.delete(gen_energy_list,mask)
    cost_list_list = np.delete(cost_list,mask)

    # print(energy_list)
    energy_graph(energy_list,x,y) #graphs annual energy of a turbine
    power_graph(power_list,x,y) #graphs average power collected by a turbine
    speed_graph(speed_list,x,y) #graphs average speed of wind
    velocity_graph(velocity_list,x,y) #graphs average velocity of wind collected by a turbine
    speed_proportion_graph(velocity_list, speed_list,x,y) #graphs velocity divided by speed
    power_proportion_graph(power_list, potential_power_list,x,y) #graphs power divided by total possible power proportion

if __name__ == '__main__':
    name = 'paralell test'
    state = 'California'
    load_graphs_state_basic(name,state)

    # name = 'solar_data' #needs to be small data
    # solar_name = 'solar' #don't change
    # gen_size = '5'
    # cutoff = False
    # load_graphs_capacity(name,solar_name,gen_size,cutoff)
