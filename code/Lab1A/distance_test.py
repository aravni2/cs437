import time
import picar_4wd as fc

start_time = time.time()
# # fc.forward(25)
# time.sleep(4)
# def forward(power):
#     fc.left_front.set_power(power)
#     fc.left_rear.set_power(power)
#     fc.right_front.set_power(power+10)
#     fc.right_rear.set_power(power+10)

# def backward(power):
#     left_front.set_power(-power)
#     left_rear.set_power(-power)
#     right_front.set_power(-power)
#     right_rear.set_power(-power)

# def turn_left(power):
#     left_front.set_power(-power)
#     left_rear.set_power(-power)
#     right_front.set_power(power)
#     right_rear.set_power(power)

# def turn_right(power):
#     left_front.set_power(power)
#     left_rear.set_power(power)
#     right_front.set_power(-power)
#     right_rear.set_power(-power)

# def stop():
#     left_front.set_power(0)
#     left_rear.set_power(0)
#     right_front.set_power(0)
#     right_rear.set_power(0)
end_time = 0
# print (end_time-start_time)

# start_time = time.time()
# while (end_time-start_time)<=2.15:
#     fc.forward(70)
#     end_time= time.time()
# print(end_time-start_time)
# fc.stop()

# carpet
# speed = 2.25/100
# dist = 100
# fc.forward(70)
# time.sleep(speed*dist)
# fc.stop()

# hardwood
speed = 2.15/100
dist = 50
fc.forward(70)
time.sleep(speed*dist)
fc.stop()


# 360 turns
# 3 for carpet
#2.35 for hardwood

