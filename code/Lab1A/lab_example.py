import picar_4wd as fc
import time

def move25():
    speed4 = fc.Speed(25)
    speed4.start()
    fc.forward(25)
    x=0
    for i in range(4):
        time.sleep(1.75)
        speed=speed4()
        x+=speed*1
        print(f"{speed}mm/s")
    print(f"{x}mm")
    speed4.deinit()
    fc.stop()

if __name__ == '__main__':
    start= time.start()
    stop = 4
    