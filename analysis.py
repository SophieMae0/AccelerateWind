from matplotlib import pyplot as plt
import pickle
from dump import *
from calc import *
from load import *
from graph import *


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
    percent_list = np.array(percent_list)*100/len(power_list)

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
    (x,y,energy_list,angle_list,power_list,speed_list,velocity_list,gen_energy_list,cost_list) = load_pickles_basic(name)
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


def power_cost(name,bucket_size,max_velocity):
    """prints the frequency that each average power falls within a range the size of bucket_size
       also graphs the distribution of average powers
    Inputs: name: string that was used to label the files when loading them
            bucket_size: range in Watts of average power that will be bucketed together
            max_power: max wind speed (m/s) the min generator could capture
    """
    #loading all lists stored in load_pickles_basic
    (x,y,energy_list,angle_list,power_list,speed_list,velocity_list,gen_energy_list,cost_list,velocity2_list) = load_pickles_basic(name)
    #creating a list that will hold the percentage of wind
    # max_velocity = power_function(max_velocity)

    #calculating the number of different buckets there will have to be
    num_buckets = math.ceil(max_velocity/bucket_size)


    for k in range(len(velocity2_list)):
        # print('k:',k)
        # print(energy_list[k]/3600000)
        if cost_list[k]<.1 and x[k] >= 45 and y[k] >= 17:
            print(' NEW POINT')
            print('coords',x[k],y[k])
            print('cost',cost_list[k])
            print('velcoity',velocity_list[k])
            print('proportion',velocity_list[k]/speed_list[k])
            print('AEP',gen_energy_list[k]/(3600000))
            print('capacity',((gen_energy_list[k]/3600000)/(8760*5)))
            #
            # # cost_graph(cost_list[k],x[k],y[k])
            # all_velocity = velocity2_list[k]/1.6
            # percent_list = []
            # for i in range(num_buckets): #for each bucket
            #     percent_list.append(0) #each bucket starts with 0 percent
            #     for velocity in all_velocity: #for each coordinates average power
            #         #if an average power is within the range of the current bucket
            #         if velocity >= i*bucket_size and velocity < (i+1)*bucket_size:
            #             #adds a count to the percentage list
            #             percent_list[i] += 1
            #
            # #converting to percent by dividing by number of coordinates and multiplying by 100
            # percent_list = np.array(percent_list)*100/len(all_velocity)
            #
            # for i in range(num_buckets): #for each bucket
            #     if percent_list[i] != 0: #if the percent is not 0
            #         #prints the percetnage of weather sites whose average power fall within the cuttent bucket
            #         #print(percent_list[i],'percent of weather sites between',i*bucket_size,'m/s and',(i+1)*bucket_size, 'm/s \n')
            #         pass
            #
            # ##AVERAGE POWER DISTRUBUTION HISTOGRAM
            # plt.hist(all_velocity, bins = num_buckets,range = (0,max_velocity)) #creates histogram
            # plt.title('Frequency of Power at Different Coordinates', fontsize = 25) #adds title
            # plt.xlabel('Average Power (Watts)', fontsize = 20) #labels x axis as longitude
            # plt.ylabel('Number of Locations', fontsize = 20) #labels y axis as latitude
            # plt.xticks(fontsize = 15) #setting font size of x axis values
            # plt.yticks(fontsize = 15) #setting font size of y axis values
            # plt.show() #displays graph


if __name__ == '__main__':
    # power_cost('power',1,15)
    power_cost('debug2',1,14)
