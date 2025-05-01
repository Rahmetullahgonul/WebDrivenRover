import lgpio
import time

TRIG = 23  # BCM pin number (physical pin 16)
ECHO = 24  # BCM pin number (physical pin 18)

h = lgpio.gpiochip_open(0)

# Pin setup
lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)

def measure_distance():
    lgpio.gpio_write(h, TRIG, 0)
    time.sleep(0.002)

    lgpio.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)

    # Wait for echo to go high
    start_time = time.time()
    timeout = start_time + 0.04
    while lgpio.gpio_read(h, ECHO) == 0:
        start_time = time.time()
        if start_time > timeout:
            return -1

    # Wait for echo to go low
    end_time = time.time()
    timeout = end_time + 0.04
    while lgpio.gpio_read(h, ECHO) == 1:
        end_time = time.time()
        if end_time > timeout:
            return -1

    pulse_duration = end_time - start_time
    distance = pulse_duration * 17150  # in cm
    distance = round(distance, 2)

    return distance

try:
    while True:
        distance = measure_distance()
        if distance == -1:
            print("Measurement timeout")
        else:
            print("Distance: {} cm".format(distance))
        time.sleep(1)

except KeyboardInterrupt:
    print("Program terminated.")

finally:
    lgpio.gpiochip_close(h)
