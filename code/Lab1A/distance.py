import picar_4wd as fc
import time

fc.servo.set_angle(0)
while True:
    distance = fc.scan_step(0)
    print(fc.angle_distance)
    print(distance)