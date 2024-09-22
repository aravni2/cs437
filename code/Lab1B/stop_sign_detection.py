import picar_4wd as fc
import time
import numpy as np
import pandas as pd
import math 
from pydoc import text
from vilib import Vilib #adapted and referenced from Sunfounder Vilib library: https://github.com/sunfounder/vilib
from time import sleep, time, strftime, localtime, monotonic_ns
import time
import threading
import readchar
import os

#insert here for your own device, controlling the traversal control
# from picarx import Picarx


#initialization for PiCarX
# px = None
# POWER=0


#initialization for any other car
###PUT YOUR CODE HERE


#init for utility
#time in nanosecond referencing an absolute clock
start_time = monotonic_ns()

#init for traffic sign detection with OpenCV and TensorFlow Lite
traffic_sign_detection_bool=False
take_photo_counter=0

def take_photo():
    _time = strftime('%Y-%m-%d-%H-%M-%S',localtime(time()))
    name = 'photo_%s'%_time
    username = os.getlogin()

    path = f"/home/{username}/Pictures/"
    Vilib.take_photo(name, path)
    print('photo save as %s%s.jpg'%(path,name))

def traffic_sign_detection()->bool:
    global take_photo_counter
    print('traffic sign detection running')
    print ('sanity check on traffic sign type: '+ str(Vilib.detect_obj_parameter['traffic_sign_y']))
    print('traffic sign detection going for if loop')
    if ((Vilib.detect_obj_parameter['traffic_sign_acc']!=None) and (Vilib.detect_obj_parameter['traffic_sign_acc']>0)):
        if (take_photo_counter<1 and take_photo_counter>=0):
            take_photo()
            take_photo_counter=take_photo_counter+1
        traffic_sign_type=Vilib.detect_obj_parameter['traffic_sign_t']
        traffic_sign_coodinate = (Vilib.detect_obj_parameter['traffic_sign_x'],Vilib.detect_obj_parameter['traffic_sign_y'])
        traffic_sign_size = (Vilib.detect_obj_parameter['traffic_sign_w'],Vilib.detect_obj_parameter['traffic_sign_h'])
        print("[traffic_sign Detect] ","Coordinate:",traffic_sign_coodinate,"Size",traffic_sign_size)
        print('traffic sign type is: '+ str(traffic_sign_type))
        print('traffic_sign detected with accuracy: '+str(Vilib.detect_obj_parameter['traffic_sign_acc']))
        return True
    else:
        return False
    
# def PicarX_init_func():
#     px = Picarx()
#     px.set_dir_servo_angle(0)
#     px.set_cam_tilt_angle(0)
#     px.set_cam_pan_angle(0)
#     POWER=30

def PiCarX_STOP_traffic_sign_reaction():
    global POWER
    print('PiCarX_traffic_sign_reaction executed')
    fc.stop()
    # px.backward(0)
    #wait for 3 seconds due to stop sign
    time.sleep(3)
    #go until STOP sign cleared
    while traffic_sign_detection()==True:
        print('detected')
        time.sleep(1)
        fc.forward(0)
        fc.stop()
    print('PiCarX_traffic_sign_reaction execution completed, going back to main loop')

def PiCarX_normal_actions():
    print('PiCarX_normal_actions executed')

def main():
    #initialization for main section
    global take_photo_counter, start_time

    #start video streaming using Rasp Pi as host, transfer with HTTP in localhost, turn traffic_sign_detection to true
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    Vilib.traffic_detect_switch(True)

    #let the hardware warm up for 1 sec
    time.sleep(1)


    #main loop, for both traffic sign detection and Path finding
    while True:
        print('main full self driving loop running!!!')
        current_time = monotonic_ns()
        time_elapsed=(current_time-start_time)/1000000000
        print ('time elapsed in seconds: ', str(time_elapsed))

        #traffic detection logic
        traffic_sign_detection_bool=traffic_sign_detection()

        #traffic_sign_handling, will be running until traffic_sign_cleared
        if traffic_sign_detection_bool==True:
            PiCarX_STOP_traffic_sign_reaction();
            #let the car take a breather
            time.sleep(1)
        
        if traffic_sign_detection_bool==False:
            PiCarX_normal_actions();
            ###YOUR CODE HERE!!!!


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print ('exception triggered: ', e)
    finally:
        print("shutting down")
        Vilib.camera_close()
        exit();