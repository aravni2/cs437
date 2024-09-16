import picar_4wd as fc
import time
# from servo import Servo
# import servo as servo

speed = 25
line_ref = 30
# reroute counter to correct vehilce after turn
reroute = 0

def main():
    """
    Runs main program to both keep car with in road markers and detect potential hazards ahead
    """
    # set initial angle for servo at 0 which forces a straight ahead view to start
    fc.servo.set_angle(0)
    time.sleep(2)
    reroute = 0
    while True:
        # run 'avoid shoulders' function to determine if vehicle is veering off road
        avoid_shoulders(speed,line_ref)

        # check distance at offset which is straight ahead
        dist = fc.get_distance_at(-9)
        print(dist)

        # test if cars front bumper is too close to object (within 7mm)
        if (dist <= 7) and (dist >= 0):
            print('reroute')
            # stop and backup
            manuever(speed)

            # fast turn right (default) with enough time and angle to make significant re-route
            fc.turn_right(speed*2)
            time.sleep(1.2)
            # use reroute counter to keep track of turns needed to correct path
            reroute+=1
            print('increase reroute:',reroute)
    
        # if not in danger of crashing, attempt to correct new path if re-route counter >=1
        elif reroute >= 1:
            
            fc.forward(speed)
            time.sleep(1.2)
            # correct for initial reroute turn
            fc.turn_left(speed*2)
            time.sleep(1.2)
            reroute-=1
            print('decrease reroute', reroute)
        else:
            fc.forward(speed)
        # follow_road()
        # avoid_shoulders(speed,line_ref)
        
        print("counter:",reroute)

def manuever(speed):
    """ Function that handles stopping and backing up when distance to another object is close

    Args:
        speed (int): integer sent to motor denoting level of speed
    """
    fc.stop()
    time.sleep(.2)
    fc.backward(speed*2)
    time.sleep(1.2)
    # fc.stop()
    return




def avoid_shoulders(speed, line_ref):
    """function to check picar is within lanes and correct course
        if it's detected the car is veering off

    Args:
        speed (int): integer sent to motor denoting level of speed
        line_ref (int): integer denoting the threshold level of needing to turn
                        the closer to 0, the more black is seen and denotes
    """
    
    gs_list = fc.get_grayscale_list()
    print(gs_list)
    # fc.forward(Track_line_speed)
    
    # correct car when near perpendicular to traffic lane
    if fc.get_line_status(line_ref,gs_list) == 0:
        print('crossover')
        # test whether left or right grayscale sensor is more dark and turn in opposite direction
        if gs_list[0] <= gs_list[2]:
            fc.turn_right(speed*2)
            time.sleep(.6)
        elif gs_list[2] <= gs_list[0]:
            fc.turn_left(speed*2)
            time.sleep(.6)
        # fc.forward(Track_line_speed) 
        pass
    # test right grayscale sensor for threshold and turn left if under
    # This sensor seems to be 10 points higher than the others on avg, so a correction is added
    elif gs_list[2] < line_ref+10:
        print('avoid shoulder, turn left')
        fc.turn_left(speed*2) 
        time.sleep(.6)

    # test right grayscale sensor for threshold and turn right if under
    elif gs_list[0] <= line_ref:
        print('avoid median, turn right)')
        fc.turn_right(speed*2)
        time.sleep(.6)
    


if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()