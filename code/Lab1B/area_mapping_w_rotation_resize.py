import picar_4wd as fc
import time
import numpy as np
import pandas as pd
import math 
import scipy as sc
import cv2
from tflite_runtime import interpreter
from a_star_utils import a_star_search_returnPath,a_star_search_returnMap
import stop_sign_detection as ssd
from vilib import Vilib

# # Ultrasonic
ANGLE_RANGE = 140
STEP = 1
us_step = STEP
angle_distance = [0,0]
current_angle = 0
max_angle = ANGLE_RANGE/2
min_angle = -ANGLE_RANGE/2
scan_list = []

errors = []

# car positions /////////////////////////
global facing_angle, angle_rel, car_x, car_y, arr,arr_x,arr_y,turn_time_per_rad,speed,dist
global dist_to_target, scan_count, traffic_sign_detection_bool

# absolute value of cars angle to vertical (starts facing 90)
facing_angle = math.pi/2
facing_dir = 'North'

traffic_sign_detection_bool= False
# rotation of last car turn
angle_rel = 0

# car starting point
car_x = 100
car_y = 40

# target postion
target_x = 105
target_y = 30
dist_to_target = math.sqrt((car_y-target_y)**2+(car_x-target_x)**2)
print(dist_to_target)

# calibrated values (carpeting)
# 3.1 carpet, 2.35 hardwood
turn_time_per_rad = 2.35/(math.pi*2)

# carpet speed at 70 power
# speed = 2.25/100
# hardwood speed at 70 power

speed = 2.15/100
dist=10
scan_count = 0


arr_x = 200
arr_y = 50
arr = np.zeros((arr_y,arr_x)).astype(bool)

def turn_right_90():
    global facing_angle
    fc.turn_right(70)
    time.sleep(turn_time_per_rad*(math.pi/2))
    fc.stop()
    facing_angle -= math.pi/2


def turn_left_90():
    global facing_angle
    fc.turn_left(70)
    time.sleep(turn_time_per_rad*(math.pi/2))
    fc.stop()
    facing_angle +=math.pi/2


def forward(dist):
    traffic_sign_detection_bool=ssd.traffic_sign_detection()
    if traffic_sign_detection_bool==True:
        ssd.PiCarX_STOP_traffic_sign_reaction(traffic_sign_detection_bool)
    fc.forward(70)
    time.sleep(speed*dist)
    fc.stop()
    update_pos(dist)
    print("car position:", (car_x,car_y))

def update_pos(dist):
    global car_x,car_y,target_x,target_y,dist_to_target
    if facing_angle == 0:
        car_x += int(dist/10)
    if facing_angle == math.pi/2:
        car_y -= int(dist/10)
    if facing_angle == (math.pi):
        car_x -= int(dist/10)
    if facing_angle == (math.pi*(3/2)):
        car_y += int(dist/10)
    dist_to_target = math.sqrt((car_y-target_y)**2+(car_x-target_x)**2)
    print(dist_to_target)


def navigate_astar(astar_arr):
    global facing_angle
    for point in astar_arr:
        # if facing NORTH
        if facing_angle == math.pi/2:
            # if forward
            if ((car_y > point[0]) and (car_x==point[1])):
                forward(10)
            # turning right
            if ((car_y==point[0]) and (car_x < point[1])):
                turn_right_90()
                return
            if ((car_y==point[0]) and (car_x > point[1])):
                turn_left_90()
                return
        # if facing EAST
        if facing_angle == 0:
            # if forward
            if ((car_y == point[0]) and (car_x < point[1])):
                forward(10)
            # turning right
            if ((car_y < point[0]) and (car_x == point[1])):
                turn_right_90()
                return
            # turn left
            if ((car_y > point[0]) and (car_x == point[1])):
                turn_left_90()
                return
        # if facing WEST
        if facing_angle == (math.pi):
            # if forward
            if ((car_y == point[0]) and (car_x > point[1])):
                forward(10)
            # turning right
            if (car_y > point[0]) and (car_x == point[1]):
                turn_right_90()
                return
            # turn left
            if (car_y < point[0]) and (car_x == point[1]):
                turn_left_90()
                return
        # if facing SOUTH
        if facing_angle == (math.pi*(3/2)):
             # if forward
            if ((car_y < point[0]) and (car_x==point[1])):
                forward(10)
            # turning right
            if ((car_y==point[0]) and (car_x > point[1])):
                turn_right_90()
                return
            if (car_y==point[0]) and (car_x < point[1]):
                turn_left_90()
                return
            
            


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


def plot_points(arr,x_pos,y_pos):
    if (angle_distance[1] < 150) and (angle_distance[1]>=0):
            # arr[y_pos,x_pos] = scan_count
            arr[y_pos,x_pos] = 1

def scan_area():
    global scan_count
    scan_count+=1
    fc.servo.set_angle(0)
    time.sleep(1)
    # print(arr)
    
    for _ in range(290):

        # scan local distances from ultrasonic sensor
        distance = scan_step(35)
        # convert angles to radians
        rads = (angle_distance[0]* math.pi)/180
        # print("angle of read:",rads)

        # get x and y points from distance  and angle, converted to decmeters
        x_obj = math.ceil(math.cos(rads)*angle_distance[1]/10)
        y_obj = math.ceil(math.sin(rads)*angle_distance[1]/10)


        # print("local:", angle_distance)
        # print("local x,y:", [x_obj,y_obj])
        
        # find new location of objects relative to cars position and angle
        x_rt,y_rt = rotate_transform(facing_angle,angle_rel, car_x,car_y,x_obj,y_obj)

        
        # print(angle_distance,x_rt,y_rt)

        # if angle_distance[0] <0:
        #     x_pos = 100+ x_rt

        # if angle_distance[0] >=0:
        #     x_pos = 100- x_rt

        x_pos = car_x+x_rt
        y_pos = car_y-y_rt

        print("x,y new" ,x_pos,y_pos)        

        # plot coordinates on large array
        plot_points(arr,x_pos,y_pos)


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

# testing

print('main full self driving loop running!!!')
#     current_time = monotonic_ns()

# ADD TO MAIN
# scan_area()

# astar_array = arr.astype(bool)
# astar_array = (~arr).astype(int)

# astar_arr = a_star_search_returnPath(astar_array,(car_y,car_x),(target_y,target_x))
# print(astar_arr)
# maze =a_star_search_returnMap(astar_array,(car_y,car_x),(target_y,target_x))
# maze=np.asarray(maze).astype(int)
# np.savetxt("maze.csv", maze.astype(int), fmt='%s', delimiter=",")
# navigate_astar(astar_arr)
# ///////////////////////

# forward(dist)
# time.sleep(1)
# arr[car_y,car_x] = 88882
# turn_right_90()
# forward(dist)
# arr[car_y,car_x] = 88883
# time.sleep(1)
# turn_left_90()
# forward(dist)
# arr[car_y,car_x] = 88884
# time.sleep(1)
# turn_right_90()


# ADD TO MAIN
# b = sc.ndimage.binary_dilation(arr,[
#     [ 1, 1],
#     [1, 1]
# ])
# c = sc.ndimage.binary_erosion(b,[
#     [1, 1],
#     [ 1, 1]
# ])
# # test regular array
# df= pd.DataFrame(arr)
# df.to_csv('test.csv')

# # test dilation/padding
# df = pd.DataFrame(b.astype(int))
# df.to_csv('test_pad.csv')

# # test erosion
# df = pd.DataFrame(c.astype(int))
# df.to_csv('test_contour.csv')
# //////////////////////////////
#start video streaming using Rasp Pi as host, transfer with HTTP in localhost, turn traffic_sign_detection to true
Vilib.camera_start(vflip=False,hflip=False)
Vilib.display(local=True,web=True)
Vilib.traffic_detect_switch(True)

#let the hardware warm up for 1 sec
time.sleep(1)
scan_count=0
# #main loop, for both traffic sign detection and Path finding
while True:
       #initialization for main section
    global take_photo_counter, start_time
    time.sleep(1)
    #start video streaming using Rasp Pi as host, transfer with HTTP in localhost, turn traffic_sign_detection to true

    # print('main full self driving loop running!!!')
    # current_time = time.timemonotonic_ns()
    # time_elapsed=(current_time-start_time)/1000000000
    # print ('time elapsed in seconds: ', str(time_elapsed))

    #traffic detection logic
    traffic_sign_detection_bool=ssd.traffic_sign_detection()


    #traffic_sign_handling, will be running until traffic_sign_cleared
    if traffic_sign_detection_bool==True:
        # global stop_sleep_time
        print('main loop traffic_sign_detection loop hit!!!')
        ssd.PiCarX_STOP_traffic_sign_reaction(traffic_sign_detection_bool);

    # scan terrain for objects
    scan_area()
    scan_count+=1

    # retrieve astar mapping to guide navigation, save map for diagnostics
    astar_array = arr.astype(bool)
    astar_array = (~arr).astype(int)
    
    astar_arr = a_star_search_returnPath(astar_array,(car_y,car_x),(target_y,target_x))
    print(astar_arr)
    maze =a_star_search_returnMap(astar_array,(car_y,car_x),(target_y,target_x))
    maze=np.asarray(maze).astype(int)
    np.savetxt(f"maze{scan_count}.csv", maze.astype(int), fmt='%s', delimiter=",")
    navigate_astar(astar_arr)

    dilation = sc.ndimage.binary_dilation(arr,[
    [ 1, 1],
    [1, 1]
    ])
    erosion = sc.ndimage.binary_erosion(b,[
        [1, 1],
        [ 1, 1]
    ])
    # test regular array
    df= pd.DataFrame(arr)
    df.to_csv('test.csv')

    # test dilation/padding
    df = pd.DataFrame(dilation.astype(int))
    df.to_csv('test_pad.csv')

    # test erosion
    df = pd.DataFrame(erosion.astype(int))
    df.to_csv('test_contour.csv')

#         #car go for 3 blocks
#         #adjust for the travel required after the stop sign, drive forward after for 3 secs needs to be counted. 
#         #This 3 secs is synced with the stop_sleep_time, thus the out of the order variable name
#         length_path-(stop_sleep_time)

#         #let the car take a breather
#         sleep(1)

    
#     if traffic_sign_detection_bool==False:
#         # CODE BELOW NOT TESTED YET
#         '''
#         scan_area()
#         plot
#         astar
#         astar_navigation

#         '''
#         if (length_path<=0):
#             #make Car turn function required here!!!!!!!
#             # local_map=a_star_algorithm.a_star_search_returnMap(absolute_map,start_coordinate_local_map,stop_coordinate_local_map)
#             # absolute_map=a_star_algorithm.a_star_search_returnMap(absolute_map,start_coordinate_absolute_map,stop_coordinate_absolute_map)

#             # If turning, then recalculate shortest path and length of the specified path, to be feed into the forward control
#             if next_direction!='starting':
#                 PiCarX_rotate(next_direction);
            
#             #always scan and register obstacle in absolute map when length of travel required done
#             PiCarX_scan();

#             #recalculate the shortest path from the current_coordinate
#             next_path=a_star_algorithm.a_star_search_returnPath(absolute_map,current_coordinate,stop_coordinate_absolute_map)
#             #grab length required to travel, convert it as to seconds for forward control
#             for index, coordinate in next_path:
#                 #check for the  difference in first tuple component, if negative = needs to go up; if positive = needs to go down
#                 if (next_path[0][index+1][0]-next_path[0][index][0])>0:
#                     if (current_direction=='starting' or current_direction=='down'):
#                         length_path+=1
#                         current_direction='down'
#                     else:
#                         next_direction='down'
#                         stop_coordinate_temp_map=next_path[0][index]
#                         break

#                 elif (next_path[0][index+1][0]-next_path[0][index][0])<0:
#                     if (current_direction=='starting' or current_direction=='up'):
#                         length_path+=1
#                         current_direction='up'
#                     else:
#                         next_direction='up'
#                         stop_coordinate_temp_map=next_path[0][index]
#                         break

#                 #check for the  difference in second tuple component, if negative = needs to go right; if positive = needs to go left
#                 elif (next_path[0][index+1][1]-next_path[0][index][1])>0:
#                     if (current_direction=='starting' or current_direction=='left'):
#                         length_path+=1
#                         current_direction='left'
#                     else:
#                         next_direction='left'
#                         stop_coordinate_temp_map=next_path[0][index]
#                         break

#                 elif (next_path[0][index+1][1]-next_path[0][index][1])<0:
#                     if (current_direction=='starting' or current_direction=='right'):
#                         length_path+=1
#                         current_direction='right'
#                     else:
#                         next_direction='right'
#                         stop_coordinate_temp_map=next_path[0][index]
#                         break
                
#                 else:
#                     print('something is wrong with length measurement!!!')
#                     break

#         #if Car move forward
#         temp_time_driving_anchor=monotonic_ns()
#         while ((traffic_sign_detection_bool==False) and ((monotonic_ns()-temp_time_driving_anchor)<length_path)):
#             print ('drive the car to the specified desination with directional, length, and power control')
#             # this check will break the while loop when the traffic_sign_detected, will go to the main while True loop
#             px.forward(POWER)
#             traffic_sign_detection_bool=traffic_sign_detection();
#             if traffic_sign_detection_bool==True:
#                 #update and store remaining length of travel
#                 length_path=length_path-(monotonic_ns()-temp_time_driving_anchor)

#         #when the drive is cleared as intended from the path, update the current coordinate, and rotate
#         if ((monotonic_ns()-temp_time_driving_anchor)>length_path):
#             current_coordinate=stop_coordinate_temp_map #track the last coordinate the car should stop at, forward loop, no feedback control loop, careful

#         ###YOUR CODE HERE!!!!
#         sleep(1)

# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print ('exception triggered: ', e)
#     finally:
#         print("shutting down")
#         Vilib.camera_close()
#         exit();