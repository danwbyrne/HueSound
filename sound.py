import pyaudio
import numpy as np
import time
import matplotlib.pyplot as plt


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

class StereoReader():

    def __init__(self):
        self.audio      = pyaudio.PyAudio()
        self.stream     = None
        self.data       = []
        self.chunksize  = 2048
        self.channels   = 1
        self.samplerate = 44100
        self.format     = pyaudio.paInt16
        self.device_id  = 1

    def start_recording(self):

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.stream = self.audio.open(
                        format = self.format,
                        channels = self.channels,
                        rate = self.samplerate,
                        input = True,
                        frames_per_buffer = self.chunksize,
                        input_device_index = self.device_id)
        
    def process_recording(self):
        data = self.stream.read(self.chunksize)
        nums = np.fromstring(data, np.int16)
        fftData = np.fft.rfft(nums)
        print fftData

    def stop_recording(self):
        self.stream.stop_stream()
        self.stream.close()

    def test(self):
        self.start_recording()
        self.process_recording()
        self.stop_recording()

if __name__ == "__main__":
    dev = StereoReader()
    dev.test()
    raw_input()

