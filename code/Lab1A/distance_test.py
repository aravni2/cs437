import time
import picar_4wd as fc

# start_time = time.time()
# # fc.forward(25)
# time.sleep(4)


# print (end_time-start_time)

start_time = time.time()
while (end_time-start_time)<=4:
    fc.forward(25)
    end_time= time.time()