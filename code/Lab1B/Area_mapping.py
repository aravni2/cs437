import picar_4wd as fc
import time
import numpy as np
import pandas as pd
import math 
import scipy as sc
import cv2
from tflite_runtime import interpreter

# # Ultrasonic
ANGLE_RANGE = 180
STEP = 5
us_step = STEP
angle_distance = [0,0]
current_angle = 0
max_angle = ANGLE_RANGE/2
min_angle = -ANGLE_RANGE/2
scan_list = []

errors = []





def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    # print(result)
    # print(status)
    return status, result


def do(msg="", cmd=""):
    print(" - %s..." % (msg), end='\r')
    print(" - %s... " % (msg), end='')
    status, result = eval(cmd)
    # print(status, result)
    if status == 0 or status == None or result == "":
        print('Done')
    else:
        print('Error')
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))

def get_distance_at(angle):
    global angle_distance
    fc.servo.set_angle(angle)
    time.sleep(0.04)
    distance = fc.us.get_distance()
    angle_distance = [angle, distance]
    print(distance)
    return distance

def get_status_at(angle, ref1=35, ref2=10):
    dist = get_distance_at(angle)
    if dist > ref1 or dist == -2:
        return 2
    elif dist > ref2:
        return 1
    else:
        return 0

def scan_step(ref):
    global scan_list, current_angle, us_step
    current_angle += us_step
    if current_angle >= max_angle:
        current_angle = max_angle
        us_step = -STEP
    elif current_angle <= min_angle:
        current_angle = min_angle
        us_step = STEP
    status = get_status_at(current_angle, ref1=ref)#ref1

    scan_list.append(status)
    if current_angle == min_angle or current_angle == max_angle:
        if us_step < 0:
            # print("reverse")
            scan_list.reverse()
        print(scan_list)
        tmp = scan_list.copy()
        scan_list = []
        return tmp
    else:
        return False
    


fc.servo.set_angle(0)
time.sleep(1)
arr = np.zeros((100,200))
print(arr)
count = 0
while count <100:
    distance = scan_step(35)
    rads = (angle_distance[0]* math.pi)/180
    print(rads)
    if angle_distance[0] <0:
        x_obj = int(math.sin(abs(rads))*angle_distance[1])+100

    if angle_distance[0] >=0:
        x_obj = 100- int(math.sin(abs(rads))*angle_distance[1])


    y_obj = 99-int(math.cos(abs(rads))*angle_distance[1])
    print(angle_distance,x_obj,y_obj)
    # print(angle_distance[1])
    if (angle_distance[1] < 100) and (angle_distance[1]>=0):
        # input distance values
        # arr[y,x]=angle_distance[1]
        arr[y_obj,x_obj] = 1
        print(arr)
    count+=1
b = sc.ndimage.binary_dilation(arr,[
    [0, 0, 0],
    [ 1, 1,  1],
    [1, 1, 1],
])
c = sc.ndimage.binary_erosion(b,[
    [0, 1, 0],
    [ 1, 1,  1],
    [0, 1, 0],
])
# test regular array
df= pd.DataFrame(arr)
df.to_csv('test.csv')

# test dilation/padding
df = pd.DataFrame(b.astype(int))
df.to_csv('test_pad.csv')

# test erosion
df = pd.DataFrame(c.astype(int))
df.to_csv('test_contour.csv')
