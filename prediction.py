import memory_profiler
import numpy as np
import datetime
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import sklearn
import math as math

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
    angle1 = np.where(angle<=3*math.pi/4,1,0)
    angle1 = np.where(angle<math.pi/4,0,angle1)
    #west
    angle2 = np.where(angle<=5*math.pi/4,1,0)
    angle2 = np.where(angle<3*math.pi/4,0,angle2)
    #south
    angle3 = np.where(angle<=7*math.pi/4,1,0)
    angle3 = np.where(angle<5*math.pi,0,angle3)
    #east
    angle4 = np.where(angle>7*math.pi/4,1,0)
    angle4 = np.where(angle<=math.pi/4,0,angle4)

    #deletes values that are now categorical
    #also deletes power because it is directly proportional to speed
    #so it is not useful for prediction
    tall_data = np.delete(tall_data,[0,1,3,4],axis = 1)
    #adds the categorical data on to the tall data
    tall_data = np.concatenate([tall_data,season1,season2,season3,season4,day1,day2,day3,day4,angle1,angle2,angle3,angle4],axis = 1)
    return tall_data

#getting data
five_min_tall,hour_tall,hour_short = get_data('(30.974873, -98.075409)', 26240)

#defining dependent and independent variables
x = np.array(five_min_tall)

direction = x[:,3]
power = x[:,4]

clean_x = categorical_var(x)

data = sklearn.model_selection.train_test_split(clean_x,test_size = 500)

data = np.array(data)

print(data[1].shape)

#x_test = np.array(x[:500,:])



#POLYNOMIAL REGRESSION
x_ = PolynomialFeatures(degree=2, include_bias=False).fit_transform(x)
x_test_ = PolynomialFeatures(degree=2, include_bias=False).fit_transform(x_test)
model2 = LinearRegression().fit(x_,y)
r_sq2 = model2.score(x_,y)
print('r2', r_sq2)
print('coefficent',model2.coef_)
y_pred2 = model2.predict(x_)
y_pred2 = np.where(y_pred2<0, 0, y_pred2)
y_test = model2.predict(x_test_)
error2 = y - y_pred2
error_test = y[:500] - y_test

def create_10m(prediction,direction,power,file_name):
    temp = np.memmap('/media/sophie/3aad97f1-cb33-412d-b7f3-a82f0fc88a34/fiveMinutes10/%s'% (file_name),mode='w+',dtype='float32',shape=(315360,3))
    temp[:,0] = five_min_short_speed
    temp[:,1] = prediction
    temp[:,2] = power
    temp.flush()

hours = 500
time = []
time2 = []

for i in range(hours):
    time.append(i)
time = np.array(time)

time2 = []
for i in range(hours + 500):
    time2.append(i)

plt.plot(time,hour_tall[0:hours,2])
plt.plot(time,hour_short[0:hours,0])
plt.show()

plt.plot(time,y_test)
plt.plot(time2,hour_short[0:hours+500,0])
#plt.show()

plt.plot(time+500,y_pred2[0:hours])
#plt.plot(500 + time,hour_short[500:hours+500,0])
plt.show()

plt.scatter(hour_tall[0:hours,2],error2[0:hours])
plt.show()
