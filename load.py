import numpy as np
import math as math
import pickle
import os
import dill
from dump import *
from calc import *

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

def load_pickles_basic(name):
    """loads energy, angle, power, speed, and velocity,generator energy and cost lists that have been pickled
    Inputs: name: string that was used to label the files when loading them
    """
    #redirecting to the file that saves generated data
    os.chdir('/media/sophie/Rapid/AccelerateWind/data')
    #loads data
    x = pickle.load(open('x.txt', 'rb'))
    y = pickle.load(open('y.txt', 'rb'))
    energy_list = np.array(pickle.load(open('energy_list_%s.txt' % (name), 'rb')))
    angle_list = np.array(pickle.load(open('angle_list_%s.txt' % (name), 'rb')))
    power_list = np.array(pickle.load(open('power_list_%s.txt' % (name), 'rb')))
    power2_list = np.array(pickle.load(open('power2_list_%s.txt' % (name), 'rb')))
    speed_list = np.array(pickle.load(open('speed_list_%s.txt' % (name), 'rb')))
    velocity_list = np.array(pickle.load(open('velocity_list_%s.txt' % (name), 'rb')))
    gen_energy_list = np.array(pickle.load(open('gen_energy_list_%s.txt' % (name), 'rb')))
    cost_list = np.array(pickle.load(open('cost_list_%s.txt' % (name), 'rb')))

    x_state = dill.load(open('x_state_%s.txt' % (name), 'rb'))
    y_state = dill.load(open('y_state_%s.txt' % (name), 'rb'))
    speed_state = dill.load(open('speed_state_%s.txt' % (name), 'rb'))
    velocity_state = dill.load(open('velocity_state_%s.txt' % (name), 'rb'))
    power_state = dill.load(open('power_state_%s.txt' % (name), 'rb'))
    power2_state = dill.load(open('power2_state_%s.txt' % (name), 'rb'))

    return (x,y,energy_list,angle_list,power_list,speed_list,velocity_list,gen_energy_list,cost_list,power2_list,x_state,y_state,speed_state,velocity_state,power_state,power2_state)


if __name__ == '__main__':
    pass
