import pyvisa as visa
import time
import matplotlib.pyplot as plt
import numpy as np
from time import sleep
from time import perf_counter
import csv
import os 
import json
from scipy.signal import butter, lfilter, freqz
from matplotlib.ticker import MultipleLocator
from win32com.client import Dispatch
from collections import deque
from scipy.fft import fft, fftfreq, rfft


def save_dictionary(data, name):
    if(name[-1] == '_'): name = name[:-1]
    name = name+'.json'
    
    with open('Dicts/' + name, 'w') as f: 
        json.dump(data, f)
    return

def open_dictionary(name):
    if(name[-1] == '_'): name = name[:-1]
    name = name+'.json'

    if os.path.isfile(name):
        with open(name, 'r') as f:
            data = json.load(f)
    else:
        with open('Dicts/' + name, 'r') as f:
            data = json.load(f)
    return data


'''
targetData: list of floats
data: list of floats
maxShift: Maximum allowed shift
plotFlag: Plot or not
nToUse: how many points of data to use
shiftIndex: Do not do any checks, and shift data and return it
'''
def shiftData(targetData, data, maxShift = 50, plotFlag = False, nToUse = 100, shiftIndex = None):
    
    if shiftIndex:
        a = shiftIndex % len(data)
        if(shiftIndex < 0):
            #d3 = d2[-a:] + d2[:-a]
            d3 = data[-a:] + [data[-1]]*abs(shiftIndex)
        elif shiftIndex==0:
            d3 = data
        else:
            d3 = [data[0]]*abs(shiftIndex) + data[:-a]        
        return d3
    
    if targetData == data: 
        return data
    
    if plotFlag:

        plt.figure(figsize=(12, 8), dpi=300)
        plt.title("Before shifting")
        plt.plot(targetData, label='Target')
        plt.plot(data, label='Data to shift')
        plt.show()

    yessir = np.empty([nToUse,1])

    if plotFlag: plt.figure(figsize=(12, 8), dpi=300)

    maxtemp = 10000
    maxi = 0
    for i in range(-maxShift,maxShift+1):
        a = i % len(data)
        if(i < 0):
            #d3 = d2[-a:] + d2[:-a]
            d3 = data[-a:] + [data[-1]]*abs(i)
        elif i==0:
            d3 = data
        else:
            d3 = [data[0]]*abs(i) + data[:-a]

        yessir.fill(i)
        temp = [float(x) - float(y) for x, y in zip(targetData[:nToUse], d3[:nToUse])]
        #temp = [float(x) - float(y) for x, y in zip(d1, d3)]

        if abs(max(temp)) + abs(min(temp)) < maxtemp: 
            permtemp = d3
            maxtemp = abs(max(temp)) + abs(min(temp))
            maxi = i
        if plotFlag: plt.scatter(yessir.tolist() , temp)

    print("Best shifting is by shifting about " + str(maxi))
    
    if plotFlag:
        ticks = np.arange(0, 101, 5)

        plt.gca().xaxis.set_major_locator(MultipleLocator(5))
        plt.gca().xaxis.set_minor_locator(MultipleLocator(1))
        plt.grid(True, 'minor', color='#eeeeee') # use a lighter color

        plt.grid()
        plt.show()

        plt.figure(figsize=(12, 8), dpi=300)
        plt.title("After shifting")
        plt.plot(targetData)
        plt.plot(permtemp)
        plt.show()
    
    return permtemp

def getCSV(fileName):
    with open(fileName, newline='') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_NONE)
        data = list(reader)
        data = [float(i) for i in data[0][:]]
    return data

def butter_lowpass(cutoff, fs, order=5):
    return butter(order, cutoff, fs=fs, btype='low', analog=False)

def butter_lowpass_filter(data, cutoff, fs, order=5):
    shift = data[0]
    data = [x-shift for x in data]
    
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    y = y.tolist()
    y = [x+shift for x in y]
    return y

def unifyData(data, maxVoltage, divisionFactor):
    unifiedData = data
    i = 0
    for d in data:
        unifiedData[i] = d*divisionFactor/maxVoltage
        i = i+1
    return unifiedData
def startAtZero(data):
    shift = np.mean(data[:80])
    data = [x-shift for x in data]
    return data

def kvToInt(x):
    if type(x) == float or type(x) == int:
        return x
    if 'k' in x or 'K' in x:
        if len(x) > 1:
            x = x.replace('V', '')
            x = x.replace('v', '')
            x = x.replace('K', '.')
            x = x.replace('k', '.')
            return int(float(x) * 1000)
        return 1000
    return 0