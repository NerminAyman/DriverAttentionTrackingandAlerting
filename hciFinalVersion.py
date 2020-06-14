import zmq
import threading
from threading import Thread
from playsound import playsound
import time
import msgpack
import keyboard

# The REQ talks to Pupil remote and receives the session unique IPC SUB PORT

ctx = zmq.Context()
pupil_remote = ctx.socket(zmq.REQ)
ip = 'localhost'  # If you talk to a different machine use its IP.
port = 50020  # The port defaults to 50020. Set in Pupil Capture GUI.
req_port = "50020"
pupil_remote.connect(f'tcp://{ip}:{port}')

# Request 'SUB_PORT' for reading data
pupil_remote.send_string('SUB_PORT')
sub_port = pupil_remote.recv_string()

# Request 'PUB_PORT' for writing data
#pupil_remote.send_string('PUB_PORT')
#pub_port = pupil_remote.recv_string()

#...continued from above
# Assumes `sub_port` to be set to the current subscription port
subscriber = ctx.socket(zmq.SUB)
subscriber.connect(f'tcp://{ip}:{sub_port}')
subscriber.subscribe('gaze.')  # receive all gaze messages

###############surface tracking environment
req = ctx.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(ip, req_port))
req.send_string('SUB_PORT')
sub_port2 = req.recv_string()
subscriberSurface = ctx.socket(zmq.SUB)
subscriberSurface.connect("tcp://{}:{}".format(ip, sub_port2))
subscriberSurface.setsockopt_string(zmq.SUBSCRIBE, 'surface')

##################


def playSound():
 playsound('alert.wav')

 

#notifyUserSound = threading.Thread(target = playSound) # thread for executing playSound function
#notifyUserSound = Thread(target = playSound)


fiveSecondsCheck = time.time() +5 # within 5 seconds if the number of frames where the confidence is 0
blinkFrames =0 #number of frames that blinking occured
unfocusedFrames=0 ## number of frames where the user is not focusing (can be blinking or any other not focusing measures)
startTime = time.time() #time since program run till break
blinkingFrames=0 #number of frames where the confidence is 0
lookingOutsideFrames = 0 ## number of frames where user is not looking on the road
lookingOutSideFlag=0 # checks if the user is looking outside for consecutive frames (this flag is used to play sound only once)
while True:
 topic, payload = subscriber.recv_multipart()
 message = msgpack.loads(payload) ####returns dictionary with data
 topic2, payload2 = subscriberSurface.recv_multipart()
 message2 = msgpack.loads(payload2)
 gaze_on_surfaces = message2[b'gaze_on_surfaces']
 if gaze_on_surfaces[0] != None:
  on_surf = gaze_on_surfaces[0]
  on_surf2 = on_surf[b'on_surf']

 
 confidence = message[b'confidence']
 baseData = message[b'base_data']
 baseDataValues = baseData[0] #base data contains an array with only one element which all data in base data
 
 ellipse = baseDataValues[b'ellipse']
 ellipseCenter = ellipse[b'center']
 ellipseCenterY = ellipseCenter[1]
 bNormPos = message[b'norm_pos'] #position in the world image frame in normalized coordinates
 yBorder = bNormPos[1] #y position in the world image frame in normalized coordinates
 programTimer = time.time() # inside while loop to keep track of total program time
##############method for checking blinking feature of user and notificaition and calculating unfocused time
 if time.time() < fiveSecondsCheck:
  if confidence < 0.25:
   blinkingFrames = blinkingFrames+1
   unfocusedFrames = unfocusedFrames + 1
   if blinkingFrames > 180:
    #print("you blink too much")
    #playsound('alert.wav')
    blinkingFrames = 0
 else:   
  fiveSecondsCheck = time.time() +5
 #print("yborder is ")
 #print(ellipseCenterY)
#################method for checking if user is not looking on the road and calculating unfocused time    
 if on_surf2 == False :
  lookingOutSideFlag=1
  lookingOutsideFrames = lookingOutsideFrames+1
  unfocusedFrames = unfocusedFrames + 1
  if lookingOutSideFlag == 1 and lookingOutsideFrames > 29 :
   #print("eyes on the road")
   #playSound()
   lookingOutsideFrames = 0
   lookingOutSideFlag =0
   
 else:
  lookingOutSideFlag= 0 
 if keyboard.is_pressed('x'):
  unfocusedTime = unfocusedFrames/32
  focusedTime = programTimer - startTime - unfocusedTime
  break
 

print("focused Time during trip")
print(focusedTime)
print("seconds")
print("unfocused Time during trip")
print(unfocusedTime)
print("seconds")

  
  
  
    
 

 
 
