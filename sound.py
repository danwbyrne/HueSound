from matplotlib import pylab #might not need this
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
import numpy as np
import pyaudio
#import hueCtrl
import time
import wave
import sys

class Visualizer():

    def __init__(self, samples, start_data): #samples is the chunksize
        self.samples  = samples
        self.x        = np.linspace(0,22050,self.samples)
        self.y        = np.linspace(-1.0,1.0, self.samples)
        self.data     = start_data
        self.prevBass = self.data[:465]
        #self.Light    = hueCtrl.Light(ID=4)
        #self.Light.setColor((0,0,0))
        

        plt.ion()
        self.fig = plt.figure()
        self.ax  = self.fig.add_subplot(111)
        self.ax.set_ylim([-1.0,1.0])
        self.ax.set_xlim([0.0,22050.0])
        self.line1, = self.ax.plot(self.x, start_data, 'bo', ms=0.5)

    def update(self, data):
        self.line1.set_ydata(data)
        #self.jumpCheck(data[:465])
        self.fig.canvas.draw()

    def jumpCheck(self, newBass):
        d1 = self.prevBass.tolist()
        d2 = newBass.tolist()
        avgDist = 0

        if len(d1) != len(d2):
            print "$ Error in jumpCheck: len(d1) != len(d2) $"
        
        else:
            for i in range(len(d1)):
                avgDist += abs(d1[i]-d2[i])
            #print("jumpCheck Average Dist: %s" % avgDist)

            if avgDist >= 30:
                                self.Light.setBri(255*abs(newBass[200]))
                                print "setting light to: %s" % str(255*abs(newBass[200]))
                
        self.prevBass = newBass




class WavReader():

    def __init__(self, filename):
        self.chunksize  = 2048 
        self.wf         = wave.open(filename, 'rb')
        self.audio      = pyaudio.PyAudio()

        self.format     = self.audio.get_format_from_width(self.wf.getsampwidth())
        self.channels   = self.wf.getnchannels() #maybe if I get to processing 2 channels.
        self.rate       = self.wf.getframerate()

        self.stream     = self.audio.open(format=self.format,
                                        channels = self.channels,
                                        rate = self.rate,
                                        output = True,
                                        stream_callback = self.callback)

        self.animation = None
        self.FFT_MODE  = False


    def callback(self, in_data, frame_count, time_info, status):
        data    = self.wf.readframes(frame_count)
        npdata  = np.fromstring(data, dtype=np.int16)
        
        ydata  = (npdata/float(2**15))
        

        if self.animation == None:
            self.animation = Visualizer(2048, ydata)
        else:
            self.animation.update(ydata)
            while True:
                time.sleep(0.1)



        return (data, pyaudio.paContinue)

    def startStream(self):
        self.stream.start_stream()

        while self.stream.is_active():
            time.sleep(0.1)

        self.stopStream()

    def stopStream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.wf.close()



class StereoReader():

    def __init__(self):
        self.audio      = pyaudio.PyAudio()
        self.chunksize  = 2048
        self.channels   = 1
        self.samplerate = 44100
        self.format     = pyaudio.paInt16
        self.device_id  = 2
        self.animation  = None
        self.stream = self.audio.open(format = self.format,
                                    channels = self.channels,
                                    rate = self.samplerate,
                                    input = True,
                                    frames_per_buffer = self.chunksize,
                                    input_device_index = self.device_id,
                                    stream_callback = self.callback)



    def callback(self, in_data, frame_count, time_info, status):
        npdata   = np.fromstring(in_data, dtype=np.int16)


        ydata = npdata/float(2**13)


        if self.animation == None:
            self.animation = Visualizer(frame_count, ydata)
        else:
            self.animation.update(ydata)

        return (in_data, pyaudio.paContinue)

    def start_recording(self):
        print "starting stream"
        self.stream.start_stream()

        while self.stream.is_active():
            time.sleep(0.1)

        self.stop_recording()

    def stop_recording(self):
        self.stream.stop_stream()
        self.stream.close()


def list_devices():
    # List all audio input devices
    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print str(i)+'. '+dev['name']
        i += 1


if __name__ == "__main__":

    dev = WavReader("Test Songs\\Test1.wav")
    dev.startStream()
    #dev = StereoReader()
    #dev.start_recording()


    

