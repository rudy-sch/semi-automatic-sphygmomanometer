import time
import board
import busio
import lcddriver
import adafruit_ads1x15.ads1115 as ADS
import pandas as pd
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import pyaudio
import wave
import numpy as np
from scipy.signal import butter,filtfilt

GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)#Button to GPIO23/pin 18

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
record_secs = 24 # seconds to record
dev_index = 0 # device index found by p.get_device_info_by_index(ii) (0,record)
wav_output_filename = 'korotkoff.wav' # name of .wav file

audio = pyaudio.PyAudio() # create pyaudio instantiation

# create pyaudio stream
stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
 
# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0)

display = lcddriver.lcd()
tmp=[]



print("{:>5}\t{:>5}\t{:>5}".format('raw', 'v','mmhg'))

start_time = time.time()
timex=0
kondisi = True

while kondisi:
    timex=time.time()-start_time
    chan=AnalogIn(ads,ADS.P0)
    mmhg = (940.48*chan.voltage)-174.96
    mmhg_round=round(mmhg,0)
    timex_round = round (timex,0)
    print("timex= ", timex_round)
    print("{:>5}\t{:>5.2f}\t{:>5.1f}".format(chan.value, chan.voltage, mmhg))
    display.lcd_display_string("BP = %d mmHg" %mmhg_round, 1)
    if (mmhg>=160) or (timex>11):
        kondisi = False
    time.sleep(0.5)

timelist=[]
preslist=[] 


timex = 0
start_time=time.time()
push=0

print("recording")
frames = []

for ii in range(0,int((samp_rate/chunk)*record_secs)):
    data = stream.read(chunk,exception_on_overflow=False)
    frames.append(data)
    kondisi = True
    
    while kondisi:
        timex=time.time()-start_time
        chan=AnalogIn(ads,ADS.P0)
        mmhg = (940.48*chan.voltage)-184.96
        mmhg_round=round(mmhg,0)
        timex_round = round (timex,0)
        tmp.append([timex_round, mmhg_round])
        print("{:>5}\t{:>5.2f}\t{:>5.1f}".format(chan.value, chan.voltage, mmhg))
        timelist.append(timex)
        preslist.append(mmhg)
        kondisi = False
    
print("finished recording")

# stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()

# save the audio frames as .wav file
wavefile = wave.open(wav_output_filename,'wb')
wavefile.setnchannels(chans)
wavefile.setsampwidth(audio.get_sample_size(form_1))
wavefile.setframerate(samp_rate)
wavefile.writeframes(b''.join(frames))
wavefile.close()

spf=wave.open('korotkoff.wav','r')

signal=spf.readframes(-1)
suara=np.frombuffer(signal,dtype='Int16')
fs=spf.getframerate()

Timeaxis=np.linspace(0,len(suara)/fs, num=len(suara))

N = 3 #(orde)
Wn = [2/2205,30/2205] #(freq)
B,A = butter(N,Wn,btype='bandpass')
hasilfilter = filtfilt(B,A,suara)


display.lcd_clear()
GPIO.cleanup() # Clean up

plt.figure(1)
plt.plot(timelist,preslist)  

plt.figure(2)
plt.plot(Timeaxis,suara) #(data raw)

plt.figure(3)
plt.plot(Timeaxis, hasilfilter)

plt.show()
df = pd.DataFrame(tmp, columns=['time', 'mmhg'])
df.to_csv('test.csv')
