import picar_4wd as fc
import time
# from servo import Servo
# import servo as servo

speed = 30
reroute = 0
def main():
    fc.servo.set_angle(0)
    time.sleep(2)
    reroute = 0
    while True:
        scan_list = fc.scan_step(35)
        if not scan_list:
            continue

        tmp = scan_list[3:7]
        print(tmp)
        
        if tmp == [2,2]:
            fc.forward(speed)
        elif tmp != [2,2,2,2]:
            print('reroute')
            manuever(speed)
            fc.turn_right(speed)
            time.sleep(.4)
            reroute+=1
            print('increase reroute:',reroute)
        elif reroute >= 1:
            fc.forward(speed/2)
            time.sleep(.4)
            fc.turn_left(speed)
            time.sleep(.4)
            reroute-=1
            print('decrease reroute', reroute)
        else:
            fc.forward(speed)
        # follow_road()
        
        print(reroute)
def manuever(speed):
    fc.stop()
    time.sleep(.2)
    fc.backward(speed)
    time.sleep(.4)
    # fc.stop()
    return

def follow_road():
    gs_list = fc.get_grayscale_list()
    if fc.get_line_status(400,gs_list) == 0:
        fc.forward(Track_line_speed) 
    elif fc.get_line_status(400,gs_list) == -1:
        fc.turn_left(Track_line_speed)
    elif fc.get_line_status(400,gs_list) == 1:
        fc.turn_right(Track_line_speed) 



if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()