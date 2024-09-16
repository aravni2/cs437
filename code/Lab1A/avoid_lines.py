import picar_4wd as fc
import time

Track_line_speed = 20

def Track_line():
    gs_list = fc.get_grayscale_list()
    print(gs_list)
    fc.forward(Track_line_speed)
    
    
    if fc.get_line_status(30,gs_list) == 0:
        if gs_list[0] <= gs_list[2]:
            fc.turn_right(40)
            time.sleep(.6)
        elif gs_list[2] <= gs_list[0]:
            fc.turn_left(40)
            time.sleep(.6)
        # fc.forward(Track_line_speed) 
        pass
    elif fc.get_line_status(30,gs_list) == -1:
        print('avoid median, turn right)')
        fc.turn_right(Track_line_speed)
        time.sleep(.6)
        
    elif fc.get_line_status(30,gs_list) == 1:
        print('avoid shoulder, turn left')
        fc.turn_left(Track_line_speed) 
        time.sleep(.6)

if __name__=='__main__':
    try:
        while True:
            Track_line()
    finally:
        fc.stop()
        print('Program stop')