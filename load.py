import numpy as np
import math as math
import pickle
import os
import dill
from dump import *
from calc import *

def load_pickles_basic(name,pickle_folder):
    """loads energy, angle, power, speed, and velocity,generator energy and cost lists that have been pickled
    Inputs: name: string that was used to label the files when loading them
    """
    #redirecting to the file that saves generated data
    os.chdir(pickle_folder)
    #loads data
    x = pickle.load(open('x.txt_%s.txt' % (name), 'rb'))
    y = pickle.load(open('y.txt_%s.txt' % (name), 'rb'))
    energy_list = np.array(pickle.load(open('energy_list_%s.txt' % (name), 'rb')))
    angle_list = np.array(pickle.load(open('angle_list_%s.txt' % (name), 'rb')))
    power_list = np.array(pickle.load(open('power_list_%s.txt' % (name), 'rb')))
    potential_power_list = np.array(pickle.load(open('potential_power_list_%s.txt' % (name), 'rb')))
    speed_list = np.array(pickle.load(open('speed_list_%s.txt' % (name), 'rb')))
    velocity_list = np.array(pickle.load(open('velocity_list_%s.txt' % (name), 'rb')))
    gen_energy_list = np.array(pickle.load(open('gen_energy_list_%s.txt' % (name), 'rb')))
    cost_list = np.array(pickle.load(open('cost_list_%s.txt' % (name), 'rb')))
    state_list = np.array(pickle.load(open('state_list_%s.txt' % (name), 'rb')))

    return (x,y,energy_list,angle_list,power_list,potential_power_list,speed_list,velocity_list,gen_energy_list,cost_list,state_list)


if __name__ == '__main__':
    pass
