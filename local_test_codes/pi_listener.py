# -*- coding: utf-8 -*-

import requests
import time
import lgpio
from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver

AIN1, AIN2, BIN1, BIN2 = 12, 13, 20, 21
TRIG = 23
ECHO = 24
LDR = 5

h = lgpio.gpiochip_open(0)
for pin in [AIN1, AIN2, BIN1, BIN2, TRIG]:
    lgpio.gpio_claim_output(h, pin)
lgpio.gpio_claim_input(h, ECHO)
lgpio.gpio_claim_input(h, LDR)

strip = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=8).get_strip()
COLORS = {"red": (1, 0, 0), "green": (0, 1, 0), "blue": (0, 0, 1)}
LEVELS = {"low": 50, "medium": 125, "high": 255}

def stop_all():
    for pin in [AIN1, AIN2, BIN1, BIN2]:
        lgpio.tx_pwm(h, pin, 1000, 0)

def apply_command(cmd):
    stop_all()
    if cmd == "forward":
        lgpio.tx_pwm(h, AIN1, 1000, 60)
        lgpio.gpio_write(h, AIN2, 0)
        lgpio.tx_pwm(h, BIN1, 1000, 60)
        lgpio.gpio_write(h, BIN2, 0)
    elif cmd == "backward":
        lgpio.tx_pwm(h, AIN2, 1000, 60)
        lgpio.gpio_write(h, AIN1, 0)
        lgpio.tx_pwm(h, BIN2, 1000, 60)
        lgpio.gpio_write(h, BIN1, 0)
    elif cmd == "left":
        lgpio.tx_pwm(h, AIN1, 1000, 60)
        lgpio.gpio_write(h, AIN2, 0)
        lgpio.tx_pwm(h, BIN2, 1000, 60)
        lgpio.gpio_write(h, BIN1, 0)
        time.sleep(0.3)
        stop_all()
    elif cmd == "right":
        lgpio.tx_pwm(h, AIN2, 1000, 60)
        lgpio.gpio_write(h, AIN1, 0)
        lgpio.tx_pwm(h, BIN1, 1000, 60)
        lgpio.gpio_write(h, BIN2, 0)
        time.sleep(0.3)
        stop_all()
    elif cmd.startswith("led_"):
        try:
            _, color, level = cmd.split("_")
            r, g, b = COLORS.get(color, (0,0,0))
            bright = LEVELS.get(level, 0)
            strip.set_all_pixels(Color(r*bright, g*bright, b*bright))
            strip.show()
        except:
            pass
    elif cmd == "led_off":
        strip.set_all_pixels(Color(0, 0, 0))
        strip.show()
    elif cmd == "stop":
        stop_all()

def measure_distance():
    lgpio.gpio_write(h, TRIG, 0)
    time.sleep(0.002)
    lgpio.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(h, TRIG, 0)

    start_time = time.time()
    timeout = start_time + 0.04
    while lgpio.gpio_read(h, ECHO) == 0:
        start_time = time.time()
        if start_time > timeout:
            return -1

    end_time = time.time()
    timeout = end_time + 0.04
    while lgpio.gpio_read(h, ECHO) == 1:
        end_time = time.time()
        if end_time > timeout:
            return -1

    pulse_duration = end_time - start_time
    return round(pulse_duration * 17150, 2)

def read_light():
    val = lgpio.gpio_read(h, LDR)
    return "Bright" if val == 0 else "Dark"

print("Listener started...")
while True:
    try:
        r = requests.get("https://robot-api-57ew.onrender.com/get-command", timeout=5)
        cmd = r.json().get("command")
        if cmd:
            print("Command received:", cmd)
            apply_command(cmd)

        dist = measure_distance()
        light = read_light()
        requests.post("https://robot-api-57ew.onrender.com/set-status", json={
            "distance": dist,
            "light": light
        }, timeout=5)
    except Exception as e:
        print("Error:", e)
    time.sleep(1)