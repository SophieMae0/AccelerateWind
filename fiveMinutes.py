import os
import csv
import numpy as np
from collections import defaultdict
import memory_profiler
import datetime

# this script takes data downloaded from NREL and combines it so there is
# one file for each coordinate spanning 3 years

# for each coordinate in the USA (on land) the weather site closest was chosen
# for each site there are 3 files each spanning a year

# the data is stored usuing memory mapping so it takes up ledd space
# and is quicker to read and write files

def load_data():
    """Creates a file for each coordinate in the USA with three years of wind data
    original data was collected from the NREL API
    File names are coordinates as strings"""
    #number of data entries in a year
    index = (datetime.datetime(2010,1,1)-datetime.datetime(2009,1,1))/datetime.timedelta(minutes=5)
    file_count = 0
    #changes directory to where the files are
    os.chdir('/media/sophie/Samples - 1TB/AccelerateWind/Data')
    for root, dirs, files in os.walk("."): #for each file in any folder
        for filename in files:
            print('file name:' filename)
            file_count+=1
            print('file number:'file_count)
            #reading the file as a csv to pull out the coordinate
            with open("%s/%s" % (root, filename)) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",",)
                line_count = 0
                for row in csv_reader:
                    if line_count == 1:
                        long = float(row[1])
                    elif line_count == 2:
                        lat = float(row[1])
                    elif line_count == 3:
                        break
                    line_count+=1
                coordinate = (lat, long)
                print('coordinate:', coordinate)
            #adds the file to an exisiting file if this cooridinate has come up before
            #or creates a new one, places the matrix within the file based on year number
            wind_matrix = np.loadtxt(open("%s/%s" % (root, filename), "rb"), delimiter=",", skiprows=4)
            year = wind_matrix[0,0] #year that the data in the file is from
            year__start = int((year-2009)*index)
            year_index_end = int(year_index_start + index)
            #deletes year day and minute
            wind_matrix = np.delete(wind_matrix,[0,2,4],axis = 1)
            try: #tries to add to an existing coordinate file if it exists
                temp = np.memmap('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes/%s'% (str(coordinate)),mode='r+',dtype='float32',shape=(315360,8))
            except: #if the file does not exists creates a new one
                temp = np.memmap('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes/%s'% (str(coordinate)),mode='w+',dtype='float32',shape=(315360,8))
            #places matrix in original file based on the year the data was collected
            temp[year_index_start:year_index_end,:] = wind_matrix
            temp.flush()

load_data()
