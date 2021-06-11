import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy
import os
from scipy.interpolate import make_interp_spline, BSpline

def plot_aggregation(data1, data2, data3, title) -> None:
    """Plot the data related to the aggregation experiment. TODO"""
    t = len(data1)
    x1= range(t)
    x_new = np.linspace(0, t, 200)
    y1 = data1
    y2 = data2
    y3 = data3 #wandering agents
    a_BSpline = scipy.interpolate.make_interp_spline(x1, y1)
    b_BSpline = scipy.interpolate.make_interp_spline(x1, y2)
    c_BSpline = scipy.interpolate.make_interp_spline(x1, y3)
    y1_new = a_BSpline(x_new)
    y2_new = b_BSpline(x_new)
    y3_new = c_BSpline(x_new)
    plt.title('Rate of Aggregation')
    plt.plot(x_new, y1_new, label = "Site 1", color = 'red')
    plt.plot(x_new, y2_new, label = "Site 2", color = 'blue')
    plt.plot(x_new, y3_new, label = "Wandering", color = 'black', linestyle='--')
    plt.legend()
    plt.xlabel('Number of Frames'), plt.ylabel('Number of Cockroaches')
    plt.show()

data1 = [44,84,81,50,42,57,65,54,51,88]
data2 = [46,0,0,40,53,35,30,43,43,0]
data3 = [10,16,19,10,5,9,5,3,6,12]
title = 'Rate of Aggregation: Popsize 100,Same Size'

plot_aggregation(data1,data2,data3,title)

