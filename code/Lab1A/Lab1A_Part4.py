import picar_4wd as fc
import time
import random

speed = 30
turns = ['left','right']
def main():
    while True:
        # retrieve distance from sensor, offset by -9 degrees to center and fix servo
        dist = fc.get_distance_at(-9)
        
        print(dist)
        # check distances, if less than 15mm (and greater than -2), backup and pursuit a different, random path
        if (dist <= 7) and (dist >= 0):
            fc.backward(speed)
            time.sleep(.6)
            if random.choice(turns) == 'left':
                fc.turn_left(speed)
            else:
                fc.turn_right(speed)
            # random percentage of full circle turn
            slp_time = random.random()*4.3
            print("turn time:",slp_time)
            # allow turn to occur for up to 360 degrees
            time.sleep(slp_time)
            # time.sleep(random.int(0,3))

        else:
            fc.forward(speed)

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()
