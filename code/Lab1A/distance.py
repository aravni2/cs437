import picar_4wd as fc
import time

fc.servo.set_angle(0)
while True:
    distance = fc.get_distance_at(0)
    print(fc.angle_distance)
    print(distance)


# angles =[90,60,45,20,10,0,-10,-20,-45,-60,-90]

# for angle in angles:
#     distance = fc.get_distance_at(angle)
#     print(fc.angle_distance)
#     print(distance)


# fo
