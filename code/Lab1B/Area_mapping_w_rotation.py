import picar_4wd as fc
import time
import numpy as np
import pandas as pd
import math 
import scipy as sc
import cv2
from tflite_runtime import interpreter

interpreter.Interpreter()
# # Ultrasonic
ANGLE_RANGE = 180
STEP = 9
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
    # print(distance)
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

# car positions /////////////////////////
global facing_angle, angle_rel, car_x, car_y, arr,arr_x,arr_y

# absolute value of cars angle to vertical (starts facing 90)
facing_angle = math.pi/2


# rotation of last car turn


angle_rel = 0

# car starting point
car_x = 1000
car_y = 400

target_x = 100
target_y = 200

speed = 2.25/100
dist=50

arr_x = 2001
arr_y = 501
arr = np.zeros((arr_y,arr_x))

def plot_points(arr,x_pos,y_pos,num):
    if (angle_distance[1] < 100) and (angle_distance[1]>=0):
            arr[y_pos,x_pos] = num

def scan_area(num):
    fc.servo.set_angle(0)
    time.sleep(1)
    print(arr)
    
    for _ in range(100):

        # scan local distances from ultrasonic sensor
        distance = scan_step(35)
        # convert angles to radians
        rads = (angle_distance[0]* math.pi)/180
        print("angle of read:",rads)


        x_obj = int(math.cos(rads)*angle_distance[1])
        y_obj = int(math.sin(rads)*angle_distance[1])


        print("local:", angle_distance)
        print("local x,y:", [x_obj,y_obj])
        
        # find new location of objects relative to cars position and angle
        x_rt,y_rt = rotate_transform(facing_angle,angle_rel, car_x,car_y,x_obj,y_obj)

        
        print(angle_distance,x_rt,y_rt)

        # if angle_distance[0] <0:
        #     x_pos = 100+ x_rt

        # if angle_distance[0] >=0:
        #     x_pos = 100- x_rt

        x_pos = car_x+x_rt
        y_pos = car_y-y_rt

        print("x,y new" ,x_pos,y_pos)        

        # plot coordinates on large array
        plot_points(arr,x_pos,y_pos,num)


def rotate_transform(facing_angle,angle_rel, car_x,car_y,x_obj,y_obj):
    rot_angle = facing_angle+angle_rel
    print("rot_angle", rot_angle)
    x_new =int( x_obj*math.cos(rot_angle) - y_obj*math.sin(rot_angle))
    y_new =int( x_obj*math.sin(rot_angle) + y_obj*math.cos(rot_angle))

    print("rotate x,y:", (x_new,y_new))
    # x_new= x_new +car_x
    # y_new = y_new +car_y
    # print("transform x,y:", (x_new,y_new))

    return x_new,y_new


scan_area(1)

fc.forward(70)
time.sleep(speed*dist)
fc.stop()
car_y =car_y-dist
print("car plot",car_x,car_y)
scan_area(2)
fc.turn_right(70)
time.sleep(3/4.2)
fc.stop()

fc.forward(70)
time.sleep(speed*dist)
fc.stop()
car_x= car_x+dist
print(car_x,car_y)
facing_angle=0
scan_area(3)
print("car plot",car_x,car_y)


b = sc.ndimage.binary_dilation(arr,[
    [1, 1, 1],
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