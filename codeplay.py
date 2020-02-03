import time
import csv
import wave
import lcddriver
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import numpy as np
import pandas as pd
from scipy.signal import butter,filtfilt

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)#Button to GPIO23/pin 18

kondisi= True
display = lcddriver.lcd()
push= 0


while kondisi:
    filename = 'amar manual1.wav'
    print ('play')
    #Extract data and sampling rate from file
    data, fs = sf.read(filename, dtype='float32')  
    sd.play(data, fs)
    
    file = open('amar manual1.csv','r')
    readCSV = csv.reader(file)
    for row in readCSV:
        print(row)
        button_state = GPIO.input(23)
        if button_state == False:
            push +=1
            print("push = ", push)
            if push == 1:
                print ('sistol = ',row[2])
                sistol = row[2]
                display.lcd_clear()
                display.lcd_display_string(f"sistol = {sistol}", 1)
               
            elif push == 2:
                print("diastol = ", row[2])
                diastol = row[2]
                display.lcd_clear()
                display.lcd_display_string(f"diastol = {diastol}", 2)
                
                push=0
        time.sleep(0.08)
        
    status = sd.wait()  # Wait until file is done playing
    print ('finished')
    
    kondisi=False
   
spf=wave.open('amar manual1.wav','r')

signal=spf.readframes(-1)
suara=np.frombuffer(signal,dtype='Int16')
fs=spf.getframerate()
    
Timeaxis=np.linspace(0,len(suara)/fs, num=len(suara))
    
N = 3 #(orde)
Wn = [2/2205,30/2205] #(freq)
B,A = butter(N,Wn,btype='bandpass')
hasilfilter = filtfilt(B,A,suara)  


plt.figure(2)
plt.plot(Timeaxis,suara) #(data raw)

plt.figure(3)
plt.plot(Timeaxis, hasilfilter)

plt.show()