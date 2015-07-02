import pyaudio # from http://people.csail.mit.edu/hubert/pyaudio/
import hueCtrl
import audioop
import sys
import math
 
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
 
def arduino_soundlight():
    chunk    = 2048 # Change if too fast/slow, never less than 1024
    scale    = 50   # Change if too dim/bright
    exponent = 4    # Change if too little/too much difference between loud and quiet sounds
 
    # CHANGE THIS TO CORRECT INPUT DEVICE
    # Enable stereo mixing in your sound card
    # to make you sound output an input
    # Use list_devices() to list all your input devices
    device   = 1  
    
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = 44100,
                    input = True,
                    frames_per_buffer = chunk,
                    input_device_index = device)
    
    print "Starting, use Ctrl+C to stop"
    try:
        light  = hueCtrl.Light(ID=10)
        while True:
            data  = stream.read(chunk)
            rms   = audioop.rms(data, 2)

            level = min(rms / (2.0 ** 16) * scale,1.0)
            level = level**exponent 
            level = int(level * 255)

            light.setBri(level)
 
    except KeyboardInterrupt:
        pass
    finally:
        print "\nStopping"
        stream.close()
        p.terminate()
 
if __name__ == '__main__':
    #list_devices()
    arduino_soundlight()
