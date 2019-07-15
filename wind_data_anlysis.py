import xarray as xr
import cfgrib
import numpy as np
import math as math
import pickle
from matplotlib import pyplot as plt

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

#threeeDaysWind is a 3d array grib file
#1st dimension is hourly time
#2nd dimension is latitude (-90 to 90) in quarter steps
#3rd dimension is longitude (0 to 359.8) in quarter steps
ds = xr.open_dataset('threeDaysWind.grib', engine='cfgrib')

def clean_data(name_list_string):
    """Input: a list of strings that each represent the name of variable
    Output: a list of 3d arrays for each variable
    Pulls out certain variable arrays from threeDaysWind"""
    data_list = []
    for name_index in range(len(name_list_string)):
        data = ds.variables[name_list_string[name_index]].data

        #reduces data set to one point per latitude
        #721 values latitude
        for i in range(180):
             data = np.delete(data,slice(i+1,i+4),1)

        #deleting points to the south of the USA
        data = np.delete(data,slice(0,115),1)
        #deleting points to the north of the USA
        data = np.delete(data,slice(25,len(data[0,:,0])),1)

        #reduces data set to one point per longitude
        #1440 values longitude
        for i in range(360):
            data = np.delete(data,slice(i+1,i+4),2)

        #deleting points to the west of the USA
        data = np.delete(data,slice(0,235),2)
        #deleting points to the east of the USA
        data = np.delete(data,slice(59,len(data[0,0,:])),2)

        #flagging coordinates over water
        for i in range(len(data[0,:,0])): #for each latitude
            for j in range(len(data[0,0,:])): #for each longitude
                #corrects the difference between water_binary_strings
                #and threeDaysWind coordinates
                if water_binary_strings[-115-i][55+j] == '0':
                    data[:,i,j] = np.zeros(len(data[:,i,j]))

        data_list.append(data)
    return data_list

#wind speed in m/s at 10 meters up in the u vector diection
#stored as a 3darray (time,latitude,longitude)
#u10 = (clean_data(['u10'])[0])
#wind speed in m/s at 10 meters up in the v vector diection
#stored as a 3darray (time,latitude,longitude)
#v10 = (clean_data(['v10'])[0])

def speed_function(u_array,v_array):
    """Input: wind vectors in the u and v directions in m/s
    Output: wind speed in m/s"""
    speed_array = np.sqrt((u_array**2)+(v_array**2))
    return speed_array

def power_function(speed_array):
    """Input: wind speed m/s
    Output: power in J/s"""
    power_array= .5*ro*cp*area*(speed_array**3)
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
    wind_angle = np.arctan2(u_array,v_array)
    #difference between wind direction and the angle the turbine is facing
    angle_difference = abs(wind_angle - angle)
    #no loss of speed if angle difference is within specified width
    angle_difference_width = angle_difference-width/2
    angle_difference = np.where(angle_difference_width>0, angle_difference, 0)
    #velocity of the wind that can be collected by the turbine
    velocity_array = np.cos(angle_difference)*speed_array
    #if the velcity is negative it is turned to zero
    velocity_array = np.where(velocity_array>0, velocity_array, 0)
    #print('velocity',velocity_array)
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
    energy_all_angles = power_all_angles*360
    #total energy produced at each turbine at each angle
    energy_all_angles = np.sum(energy_all_angles,1)
    #determining which angle at each turbine produces the most energy
    best_energy = np.max(energy_all_angles,0)
    #creating an array of best angle per coordinate
    angle_matrix = []
    for i in range(len(energy_all_angles[0,:,0])): #latitude
        angle_matrix.append([])
        for j in range(len(energy_all_angles[0,0,:])): #longitude
            for k in range(len(energy_all_angles[:,0,0])): #angles
                #if the energy at this angle equals the maximum energy possible
                if energy_all_angles[k,i,j] == best_energy[i,j]:
                    #add this angle as the best angle for this coordinate
                    angle_matrix[i].append(2*math.pi*(k/num_angles))
                    break #has preference towards lower angles
    return angle_matrix,best_energy

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
             the sizs are equally distributed between 7 and 12
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
        max = power_function(7+(i/num_gen)*5) #max wind speeds between 7 and 12 m/s
        #power_difference will be negative if power is above max
        power_difference = max - power_array
        #if power_difference is negative power is set to max
        new_power = np.where(power_difference>=0, power_array, max)
        #convert to energy (J)
        new_energy = new_power*360
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
    best_gen_list = [] #generator size
    best_percent_list = [] #percentage of optimal energy produces with that generator
    for i in range(len(percent_all_gen[0,:,0])): #latitude
        best_gen_list.append([])
        best_percent_list.append([])
        for j in range(len(percent_all_gen[0,0,:])): #longitude
            for k in range(num_gen): #generator size
                above_best = True #true if all percentages are above best percentage
                #if the current percentage equals the second best percentage for that coordinate
                if percent_all_gen[k,i,j] == second_best_percent[i,j]:
                    #checking for water
                    if second_best_percent[i,j] == 0:
                        #setting water coordinates to 0
                        best_percent_list[i].append(0)
                        best_gen_list[i].append(0)
                    #if second best percent is the highest generator
                    elif k == num_gen-1:
                        best_percent_list[i].append(percent_all_gen[k,i,j])
                        best_gen_list[i].append(7+((k)/num_gen)*5)
                    #best gen is one greater than second best
                    else:
                        best_percent_list[i].append(percent_all_gen[k+1,i,j])
                        best_gen_list[i].append(7+((k+1)/num_gen)*5)
                    above_best = False
                    break
            #if all percentages are above best percent
            if above_best:
                #adding the lowest percentage
                best_percent_list[i].append(percent_all_gen[0,i,j])
                best_gen_list[i].append(7+((0)/num_gen)*6)
    return np.array([best_gen_list,best_percent_list])

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




print(weibull_distribution(u10,v10,16,math.pi/2,))




gen2 = generator_classification(u10,v10,16,math.pi/2,10,.8)

testu = np.array([[[-1,2],[3,4]],[[-5,6],[7,8]]])
testv = np.array([[[-9,10],[11,12]],[[-13,14],[15,16]]])

gen = all_generators_energy(u10,v10,16,math.pi/2,5)

info = coordinate_info(u10,v10,16,math.pi/2)


x = []
y = []
s = [] #angles
s2 = [] #energy
s3 = [] #percent captured by one gen
s4 = []
c = []
c2 = []
for i in range(59):
    for j in range(25):
            x.append(i)
            y.append(j)
            s.append(info[0][0][j][i])
            s2.append(info[0][1][j][i]/(700*360))
            s3.append(gen[1][j,i]*30)
            s4.append(gen2[0][j][i]*3)
            #WIND directions
            if info[0][0][j][i] <= math.pi/4:
                c.append('blue') #from the east
            elif info[0][0][j][i] <= (math.pi/4)*3:
                c.append('green') #from the north
            elif info[0][0][j][i] <= (math.pi/4)*5:
                c.append('yellow') #from the east
            elif info[0][0][j][i] <= (math.pi/4)*7:
                c.append('red') #from the south
            else:
                c.append('blue')
            #GENERATOR size
            if gen2[0][j,i] <= 8:
                c2.append('blue')
            elif gen2[0][j,i] <= 9:
                c2.append('green')
            elif gen2[0][j,i] <= 10:
                c2.append('yellow')
            elif gen2[0][j,i] <= 11:
                c2.append('orange')
            elif gen2[0][j,i] <= 12:
                c2.append('red')

#creates scatterplot
plt.scatter(x,y,s = s4,label = 'dot',c = c2)
#adds title
plt.title('look at this graph', fontsize = 25)
#adds axis
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.xlabel('x', fontsize = 20)
plt.ylabel('y', fontsize = 20)
#adds legend
plt.legend(loc=3)

plt.show()



#creates scatterplot
plt.scatter(x,y,s = s2,label = 'dot',c = c)
#adds title
plt.title('look at this graph', fontsize = 25)
#adds axis
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.xlabel('x', fontsize = 20)
plt.ylabel('y', fontsize = 20)
#adds legend
plt.legend(loc=3)

plt.show()



#creates scatterplot
plt.scatter(x,y,s = s3,label = 'dot',c = c)
#adds title
plt.title('look at this graph', fontsize = 25)
#adds axis
plt.xticks(fontsize = 20)
plt.yticks(fontsize = 20)
plt.xlabel('x', fontsize = 20)
plt.ylabel('y', fontsize = 20)
#adds legend
plt.legend(loc=3)

plt.show()


#uncomment these lines the first time you read the data
#pickle.dump(site_dict,open('site_dict.txt', 'wb'))

#uncomment this line when data has already been read
#site_dict = pickle.load(open('word_total.txt', 'rb'))
