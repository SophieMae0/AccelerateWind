#functions not used in dump.py, would need serious TLC to get them up to code

#FROM DUMP

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

#FROM LOAD

def load_pickles_one_gen(name):
    """loads generator sizes that capture optimal energy lists that have been pickled
    Inputs: name: string that was used to label the files when loading them
    """
    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    #loads data
    x = pickle.load(open('x.txt', 'rb'))
    y = pickle.load(open('y.txt', 'rb'))
    gen_list = pickle.load(open('gen_list_%s.txt' % (name), 'rb'))
    percent_list = pickle.load(open('percent_list_%s.txt' % (name), 'rb'))
    energy_list = pickle.load(open('energy_list_%s.txt' % (name), 'rb'))
    return (x,y,gen_list,percent_list,energy_list)

def load_pickles_one_fly(name):
    """loads flywheel and generator annual energy lists that have been pickled
    Inputs: name: string that was used to label the files when loading them
    """
    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
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
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    #loads data
    x = pickle.load(open('x.txt', 'rb'))
    y = pickle.load(open('y.txt', 'rb'))
    low_cost_list = pickle.load(open('low_cost_list_%s.txt' % (name), 'rb'))
    best_gen_size_list = pickle.load(open('best_gen_size_list_%s.txt' % (name), 'rb'))
    best_fly_size_list = pickle.load(open('best_fly_size_list_%s.txt' % (name), 'rb'))
    print(best_gen_size_list)
    print(best_fly_size_list)
    return (x,y,low_cost_list,best_gen_size_list,best_fly_size_list)

#GRAPH
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
    plt.xlabel('Longitude', fontsize = 20) #labels x axis as longitude20) #adds title
    plt.xlabel('Percentage of Optimal Power', fontsize = 15) #labels x axis as longitude
    plt.ylabel('Percentage of Locations', fontsize = 15) #labels y axis as latitude
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
    cbar.set_label(label = 'Generator Size (m/s)', fontsize = 20) #adds color bar labelgy_list,x,y) #graphs annual energy of a turbine
    power_graph(power_list,x,y) #graphs average power collected by a turbine
    speed_graph(speed_list,x,y) #graphs average speed of wind
    velocity_graph(velocity_list,x,y) #graphs average velocity of wind collected by a turbine
    speed_proportion_graph(velocity_list, speed_list,x,y) #graphs velocity divided by speed
    velocity_state_graph(velocity_state,speed_state,x_state,y_state,state) #graphs pne states speed proportion
    power_proportion_graph(power_list, potential_power_list,x,y) #graphs power divided by total possible power proportion
    power_state_graph(power_state,potential_power_state,x_state,y_state,state) #graphs one states power

    plt.clim(min(gen_list), max(gen_list)); #sets color bar value limits
    plt.show() #displays graph

def load_graphs_cost(name):
    """graphs lowest cost (in dollar per kilowatt hour), and their respective flywheel
    and generator sizes
    Inputs: name: string that was used to label the files when loading them
    """
    x,y,low_cost_list, best_gen_size_list,best_fly_size_list = load_pickles_cost(name)
    cost_graph(low_cost_list,x,y) #graphs lowest dollar per kilowatt cost0.
    best_gen_size_graph(best_gen_size_list,x,y) #graphs generator size with lowest cost
    best_fly_size_graph(best_fly_size_list,x,y) #graphs flywheel size with lowest cost
