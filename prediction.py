import memory_profiler
import numpy as np
import datetime
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn import svm
from scipy.integrate import simps
import sklearn
import math as math
import os
import glob
import pickle

##this script generates predicted wind speed and direction with a time step of
##5 minutes and height of 10 meters and saves them with a
##file name that is the oordinate

#begining time in 2009
start_time = (datetime.datetime(2009,1,1)-datetime.datetime(2007,1,1))/datetime.timedelta(minutes=60)
#end time in 2011
end_time = (datetime.datetime(2011,12,31)-datetime.datetime(2007,1,1))/datetime.timedelta(minutes=60)
#total hours in the 3 years
total_time = end_time-start_time


def get_data(file_name,hours):
    """Inputs: name of the file and how many hours (starting at zero) the data should spanning
       Outputs: five_min_tall: 100 meter data taken every 5 min
                hourly_tall: 100 meter data taken every hour
                hourly_short: 10 meter data taken every hour"""
    hour_short = np.memmap('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/hourly10/%s' % (file_name),mode='r+',dtype='float32',shape=(int(total_time),2))

    five_min = np.memmap('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes/%s'% (file_name),mode='r+',dtype='float32',shape=(315360,8))

    five_min_tall = five_min
    hour_tall = five_min[slice(0,(hours*12),12),:]
    hour_short = hour_short[5:hours+5,:]

    return five_min_tall,hour_tall,hour_short

def categorical_var(tall_data):
    """creates new array for each categorical variable
    with 1s where the value is true and 0s where the value is false
    for example: season1 represents winter and will be a 1 for any
    data in December, January, and Febuary and 0 all other times"""
    #splitting the 4 different seasons
    season = tall_data[:,0].reshape((-1,1))
    #winter
    season1 = np.where(season<=1,1,0)
    season1 = np.where(season>=11,1,season1)
    #spring
    season2 = np.where(season<=4,1,0)
    season2 = np.where(season<=1,0,season2)
    #summer
    season3 = np.where(season<=7,1,0)
    season3 = np.where(season<=4,0,season3)
    #fall
    season4 = np.where(season<=10,1,0)
    season4 = np.where(season<=7,0,season4)

    #splitting the day into 4 parts
    day = tall_data[:,1].reshape((-1,1))
    #midday
    day1 = np.where(day<=5,1,0)
    #evening
    day2 = np.where(day<=11,1,0)
    day2 = np.where(day<=5,0,day2)
    #night
    day3 = np.where(day<=17,1,0)
    day3 = np.where(day<=11,0,day3)
    #morning
    day4 = np.where(day>=18,1,0)

    #splitting angles into 4 directions
    angle = tall_data[:,0].reshape((-1,1))
    #north
    angle1 = np.where(angle<=135,1,0)
    angle1 = np.where(angle<45,0,angle1)
    #west
    angle2 = np.where(angle<=225,1,0)
    angle2 = np.where(angle<135,0,angle2)
    #south
    angle3 = np.where(angle<=315,1,0)
    angle3 = np.where(angle<225,0,angle3)
    #east
    angle4 = np.where(angle>315,1,0)
    angle4 = np.where(angle<=45,0,angle4)

    #deletes values that are now categorical
    #also deletes power because it is directly proportional to speed
    #so it is not useful for prediction
    tall_data = np.delete(tall_data,[0,1,3,4],axis = 1)
    #adds the categorical data on to the tall data
    tall_data = np.concatenate([tall_data,season1,season2,season3,season4,day1,day2,day3,day4,angle1,angle2,angle3,angle4],axis = 1)
    return tall_data

def poly_reg(x,y,test_size,five_min_tall):
    """Inputs:
       x: indepentant array of variables
       y: depentanr array of variables
       test_size: proportion of the data that should be the testing data
       five_min_tall:
       Outputs: prediction of wind speed at 10m with a time step of 5 min
                and mean squared error with a test set of size test_size"""
    #splitting indepentant and depentant variables into training and test sets
    x_train, x_test, y_train, y_test = np.array(sklearn.model_selection.train_test_split(x,y,test_size = test_size))
    #converting testing, training and five minuts data into a forma
    #that can be used by sklearn for predctions
    x_train = PolynomialFeatures(degree=2, include_bias=False).fit_transform(x_train)
    x_test = PolynomialFeatures(degree=2, include_bias=False).fit_transform(x_test)
    five_min_tall = PolynomialFeatures(degree=2, include_bias=False).fit_transform(five_min_tall)
    model = LinearRegression().fit(x_train,y_train)
    #calculating r squared value
    r_sq2 = model.score(x_train,y_train)
    print('r2:', r_sq2)
    y_pred = model.predict(x_test) #generates predictive model
    y_pred = np.where(y_pred<0, 0, y_pred) #prevents negative wind speed predictions
    #calulates mean squared error
    mean_sq_error = (np.sum(np.square(y_test - y_pred)))/len(y_pred)
    print('mean squared error:', mean_sq_error)
    integral_list = []
    for i in range(len(y_pred)-1):
        integral = simps(y_test[i:i+2])-simps(y_pred[i:i+2])
        integral_list.append(integral)
    mean_sq_integral = np.sum(np.square(np.array(integral_list)))/len(integral_list)
    print('mean squared integral:', mean_sq_integral)
    #retrains model on all data available
    x = PolynomialFeatures(degree=2, include_bias=False).fit_transform(x)
    final_model = LinearRegression().fit(x,y)
    #generates data for 10 meters with a time step of 5 minutes
    five_min_pred = final_model.predict(five_min_tall)
    return five_min_pred,mean_sq_error,mean_sq_integral

def create_10m(prediction,direction,file_name):
    """Inputs:
       prediction: predicted wind speed (m/s) at 10 meters based on polynomial regression
       direction: wind direction in degrees
       file_name: string coordinate of site that will be the filename
       creates a memory mapped file with predicted 10 meter wind direction and speed"""
    temp = np.memmap('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes10/%s'% (file_name),mode='w+',dtype='float32',shape=(315360,2))
    temp[:,0] = prediction
    temp[:,1] = direction
    temp.flush()

def create_all_10m():
    """creates a file for each site with a file name of its coordinant
    """
    count = 0
    os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes')
    error_list = []
    coords_list = []
    integral_list = []
    for file in glob.glob("*"): #for each file in any folder
        count +=1
        print(count)
        print(file)
        five_min_tall,hour_tall,hour_short = get_data(file,26240)
        direction = five_min_tall[:,3]
        clean_five_min= categorical_var(five_min_tall)
        clean_x = categorical_var(hour_tall)
        five_min_pred,error,integral = poly_reg(clean_x,hour_short[:,0],.3,clean_five_min)
        error_list.append(error)
        coords_list.append(eval(file))
        integral_list.append(integral)
        #create_10m(five_min_pred,direction,file)
    os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34')
    # pickle.dump(error_list,open('error_list.txt', 'wb'))
    # pickle.dump(coords_list,open('coords_list.txt', 'wb'))
    #pickle.dump(integral_list,open('integral_list.txt', 'wb'))

#create_all_10m()
#
os.chdir('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34')
error_list = pickle.load(open('error_list.txt', 'rb'))
coords_list = pickle.load(open('coords_list.txt', 'rb'))
integral_list = pickle.load(open('integral_list.txt', 'rb'))

x = []
y = []
c = []
error = []
for i in range(len(coords_list)):
    y.append(coords_list[i][0]-25)
    x.append(coords_list[i][1]+125)
    error.append(math.sqrt(error_list[i]))


plt.scatter(x,y,c=error,label = 'Weather Site',cmap = 'jet')
#adds title
plt.title('Mean Error of Predicted Velocity', fontsize = 25)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)
plt.ylabel('Latitude', fontsize = 20)
#adds legend
plt.legend(loc=3, fontsize = 15)
cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

cbar.set_label(label = 'Mean Error', fontsize = 20)
plt.clim(0, 3);
plt.show()

five_min_tall,hour_tall,hour_short = get_data('(41.888889, -113.148224)',26240)
direction = five_min_tall[:,3]
clean_five_min= categorical_var(five_min_tall)
clean_x = categorical_var(hour_tall)
clean_x = PolynomialFeatures(degree=2, include_bias=False).fit_transform(clean_x)
model = LinearRegression().fit(clean_x,hour_short[:,0])
y_pred = model.predict(clean_x)
error = hour_short[:,0]-y_pred
r_sq2 = model.score(clean_x,hour_short[:,0])
print(r_sq2)

integral_error_list = []
for i in range(len(y_pred)-1):
    integral = simps(hour_short[i:i+2,0])-simps(y_pred[i:i+2])
    #print (integral)
    integral_error_list.append(integral)


plt.scatter(x,y,c=integral_list,label = 'Weather Site',cmap = 'jet')
#adds title
plt.title('Mean Error of Predicted Velocity', fontsize = 25)
#adds axis
plt.xticks(ticks = [0,10,20,30,40,50,60], labels = [-125,-115,-105,-95,-85,-75,-65], fontsize = 15)
plt.yticks(ticks = [0,5,10,15,20,25], labels = [25,30,35,40,45,50], fontsize = 15)
plt.xlabel('Longitude', fontsize = 20)
plt.ylabel('Latitude', fontsize = 20)
#adds legend
plt.legend(loc=3, fontsize = 15)
cbar = plt.colorbar(cmap = 'jet')

cbar.ax.tick_params(labelsize=15)

cbar.set_label(label = 'Mean Error', fontsize = 20)
plt.clim(0, 3);
plt.show()


hours = 1000
time = []
time2 = []
time3 = []

# for i in range(hours):
#     time.append(i*60)
#     for j in range(12):
#         time2.append(i*60+j)
# time = np.array(time)
# time2 = np.array(time2)

for i in range(hours):
    time.append(i)
    time3.append(i+.5)

#print (integral_list[:hours])
#print('sum',np.sum(np.square(np.array(integral_list))))
#print(np.sum(np.square(np.array(integral_list)))/len(integral_list))

#polynomial regression
plt.plot(time,hour_short[:hours,0],label = 'Actual')
plt.plot(time,y_pred[:hours], label = 'Predicted')
plt.plot(time,error[:hours], label = 'Error')
plt.plot(time3,integral_error_list[:hours], label = 'Integral')

plt.title('Predicted vs Actual Wind Speed', fontsize = 25)
#adds axis
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
plt.xlabel('Hours', fontsize = 20)
plt.ylabel('Wind Speed (m/s)', fontsize = 20)

plt.legend(loc=3, fontsize = 15)

plt.show()




plt.scatter(time,direction[:hours], label = 'Integral')

plt.title('Predicted vs Actual Wind Speed', fontsize = 25)
#adds axis
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
plt.xlabel('Hours', fontsize = 20)
plt.ylabel('Wind Speed (m/s)', fontsize = 20)

plt.legend(loc=3, fontsize = 15)

plt.show()
