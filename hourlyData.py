import numpy as np
import datetime
import os
import glob
import h5pyd
from pyproj import Proj
import time
import memory_profiler

##this script uses 100 m data to download matching 10 m data from NREL api
#the new file names are their coordinants

#time that the data starts
start_time = (datetime.datetime(2009,1,1)-datetime.datetime(2007,1,1))/datetime.timedelta(minutes=60)
#time that the data enda
end_time = (datetime.datetime(2011,12,31)-datetime.datetime(2007,1,1))/datetime.timedelta(minutes=60)
#number of hours between when the data starts and ends
total_time = end_time-start_time

#changes directory to where the data is stored
os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes')

def coor_list():
    """creates a list of all the file names of the five minutes data
        each file name is a coordinate in the USA"""
    coor = []
    for file in glob.glob("*"): #for each file in any folder
        coor.append(eval(file)) #converts the file name from a string to a tuple
    return coor

#requesting data base from NREL
f = h5pyd.File("/nrel/wtk-us.h5", 'r')

#defining the cone projection (modified lambert cone)
#this projection was copied from NREL
projstring = """+proj=lcc +lat_1=30 +lat_2=60
                +lat_0=38.47240422490422 +lon_0=-96.0
                +x_0=0 +y_0=0 +ellps=sphere
                +units=m +no_defs"""

projectLcc = Proj(projstring)

#setting the origin of the cone
_origin_ll = reversed(f['coordinates'][0][0])  # Grab origin directly from database
origin = projectLcc(*_origin_ll) #projecting origin onto the cone

def convert_to_lam(coords):
    """converts a list of standard coordinates
    to an array of modified lambert cone coordinates"""
    #converting coordinate list to an array
    coords = np.array(coords)
    #inversing the coordinate tuples
    coords = np.array([coords.T[1],coords.T[0]]).T
    #projecting standard coordinates onto the modified lambert cone
    coords = np.array([projectLcc(*x) for x in coords])
    #finds the distance of the lambert coordinates from the origin
    delta = np.subtract(coords, origin)
    #scales coordinates and rounds them to a whole integer
    ij = np.array(np.round(delta/2000),dtype="int32")
    #inverses each lambert cone coordinate
    return tuple(np.array([ij.T[1],ij.T[0]]).T)

def get_data(start,num_files,coords):
    """Inputs:
       start: how many coordinates in to start at (used to run this function in parts)
       num_files: total number of coordinates
       coor: list of coordinates
       Creates a memory mapped file for each coordinate with its coordinate as a file name
       The file has 8 variables: [month, hour, speed, direction, power, temerature, pressure, density]
    """
    #converts standart coordinate names of files to an array of lambert coordinant tuples
    lam = convert_to_lam(coords)
    #converts the array of lambert cooridate tuples to 2 arrays of x coordinates and y cooridates
    lam_list = [[ i for i, j in x],
               [ j for i, j in x]]

    for i in range(start,num_files): #for each coordinant starting from start
        #breaks for 100 seconds so api requests fail less
        time.sleep(100)
        #if this function is stopped part way through the next start should be the previous i
        print(i)
        success = False #wether or not api request wne through

        while success == False: #while the api request has not gone through
            try:
                #creates memory mapped file with its standard coordinate as its file name
                #it has dimensions of [time steps, 2] and stores wind speed and direction
                temp = np.memmap('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/hourly10/%s' % (str((coords)[i])),mode='w+',dtype='float32',shape=(int(total_time),2))

                #wind speed at all times between 2009 and 2011 at all coordinants in lam_list
                temp[:,0] = f["windspeed_10m"][int(start_time):int(end_time),lam_list[0][i],lam_list[1][i]]
                #wind direction at all times between 2009 and 2011 at all coordinants in lam_list
                temp[:,1] = f["winddirection_10m"][int(start_time):int(end_time),lam_list[0][i],lam_list[1][i]]

                success = True  #api reuest has been successful
            except:
                #api request has failed
                print('try again')
                #pauses for 300 seconds then tries request agaun from the beginning of the while loop
                time.sleep(300)
        #resets temp variable
        temp.flush()


coords = coor_list()
get_data(0,len(coor),coords_list)
