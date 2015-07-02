from phue import Bridge
from PIL import Image, ImageGrab
import math, time, random, os

BRIDGE_IP          = '10.0.1.2'             #the local bridge IP.
LIGHTS             = []                     #my lights, allows for multiple lights though.
BUFF               = 7.5                    #buffer for the similar colors test.
BRIGHTNESS_PERCENT = 1                      #global brightness modifier to give a lower maximum brightness.
DEV_MODE           = False                  #Dev Mode means the lights do not communicate with the bridge (i.e no bridge required).
l,h                = 1920,1080              #the screen resolution.

COLORS = {'RED'     : (255,0,0),
          'GREEN'   : (0,255,0),
          'BLUE'    : (0,0,255),
          'MAGENTA' : (255,0,255),          #some simple colors you can use with the set_color() function in the Light class.
          'PURPLE'  : (128,0,128),
          'WHITE'   : (248,248,255),
          'YELLOW'  : (255,255,0)}


if DEV_MODE == False:                       #connects to the bridge if Dev Mode is NOT active.
    bridge = Bridge(BRIDGE_IP)
    bridge.connect()
    LIGHTS = bridge.get_light_objects('id')

#returns the brightness of a color
def getBrightness(RGB):
    bri = int((0.299*RGB[0] + 0.587*RGB[1] + 0.0722*RGB[2])*BRIGHTNESS_PERCENT)
    return bri

#EnhanceColor and getRGBtoXY are based on original code from http://stackoverflow.com/a/22649803 and https://gist.github.com/error454/6b94c46d1f7512ffe5ee
#this converts the color to more accurately perceived colors
def EnhanceColor(norm):
    if norm > 0.04045:
        return math.pow((norm + 0.055)/ (1.0 + 0.055), 2.4)
    return norm / 12.92 
    
#returns an [x,y] coordinate for an RGB color on Hue's Color Coordinate map.
def getRGBtoXY(RGB):
    #TODO: There may be a simpler way some linear algebra could speed this up, look into numpy.

    normRGB = [] #storing the colors after setting to between 0.0 and 1.0
    outRGB  = []
    
    for i in range(3):
        normRGB.append(RGB[i]/255.0)
        outRGB.append(EnhanceColor(normRGB[i]))
    
    X = outRGB[0] * 0.649926 + outRGB[1] * 0.103455 + outRGB[2] * 0.197109
    Y = outRGB[0] * 0.234327 + outRGB[1] * 0.743075 + outRGB[2] * 0.022598
    Z = outRGB[1] * 0.053077 + outRGB[2] * 1.035763
    
    if (X + Y + Z) == 0:
        return (0,0)
    else:
        xFinal = X / (X + Y + Z)
        yFinal = Y / (X + Y + Z)
        return (xFinal, yFinal)
        
#checks if the current color is similar to the color it is trying to change to using a basic distance formula.
def Similar(curr, new):
    diff = math.sqrt((curr[0]-new[0])**2 + (curr[1]-new[1])**2 + (curr[2]-new[2])**2)
    if DEV_MODE == True:
        print diff
    return diff <= BUFF

#returns the currently active lights.
#TODO: Make it print out the names of the lights and the IDs for easier assignment.
def getLights():
    for i in LIGHTS:
        print "Light " + str(i)

class Light:
    
    def __init__(self, ID=3, pollcent=[420,110], pollrad=100, polls=100):
        self.ID         = ID         #the ID of the light.
        self.PollCenter = pollcent   #the center of the polling circle.
        self.PollRadius = pollrad    #the radius for polling.
        self.POLLS      = polls      #the number of pixels it measures before making a decision.
        self.Color      = (0,0,0)    #the color of the light.
        self.Bri        = 0          #the brightness of the light.

        if DEV_MODE == False:
            self.LightObj   = LIGHTS[ID] #the phue Light Object
        
    #get-commands
    def getID(self): return self.ID
    def getLight(self): return self.LightObj
    def getPollCent(self): return self.PollCenter
    def getPollRad(self): return self.PollRadius
    def getPolls(self): return self.POLLS
    def getColor(self): return self.Color
    def getBri(self): return self.Bri
    
    #set-commands
    def setID(self,ID):
        self.ID = ID                 #sets both

        if DEV_MODE == False:
            self.LightObj = LIGHTS[self.ID]
        
    def setPollCent(self,newCent): self.PollCenter = newCent
    def setPollRad(self,newRad): self.PollRadius = newRad
    def setPolls(self,num): self.POLLS = num
    
    #sets and changes to a new color
    def setColor(self,newCol):
        if type(newCol) is str:
            newCol = newCol.upper()
            self.Color = COLORS[newCol]

        else:
            self.Color = newCol

        if DEV_MODE == False:
            self.LightObj.xy = getRGBtoXY(self.Color)

        else:
            return "Light %s set to %s" % (self.ID, self.Color)
            #TODO: Add TKinter window that physically displays the color polled, essentially a virtual Hue Light.
                
    
    #sets and changes to a different brightness
    def setBri(self, newBri):
        self.Bri = newBri

        if DEV_MODE == False:
            self.LightObj.brightness = self.Bri

        else:
            return 

        #brightness isn't neccesary for the virtual light.
        
    #polls the Lights polling area to get a new average color
    def PollScreen(self):
        sTime  = time.time()
        screen = ImageGrab.grab().load()
        RGB    = [0.0,0.0,0.0]
        
        for poll in range(self.POLLS):
            
            theta   = random.randint(0,360) * (2*math.pi)/(360)
            x       = int(self.PollCenter[0] + (self.PollRadius * math.cos(theta)))
            y       = int(self.PollCenter[1] + (self.PollRadius * math.sin(theta)))
            tempCol = screen[x,y]
            
            for i in range(3):
                RGB[i] += (tempCol[i])
                
        for i in range(3):
                    RGB[i] /= self.POLLS

        if DEV_MODE == True:
            return time.time() - sTime
                    
        return RGB
        
    #attempts to update the light.  
    def Update(self):
        newCol = self.PollScreen()
            
        if not Similar(self.Color,newCol):
            self.setColor(newCol)
            self.setBri(getBrightness(newCol))

        
    
    
