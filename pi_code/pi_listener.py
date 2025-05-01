# -*- coding: utf-8 -*-

import requests
import time
import lgpio
import threading
import pygame
import io
from gtts import gTTS
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

COLORS = {
    "red": (1, 0, 0),
    "green": (0, 1, 0),
    "blue": (0, 0, 1),
    "black": (0, 0, 0)
}

LEVELS = {
    "low": 50,
    "medium": 125,
    "high": 255
}

current_speed_pwm = 30
led_enabled = False

pygame.mixer.init()

def stop_all():
    for pin in [AIN1, AIN2, BIN1, BIN2]:
        lgpio.tx_pwm(h, pin, 1000, 0)

def welcome_animation():
    try:
        brightness = 255
        for _ in range(2):
            strip.set_all_pixels(Color(brightness, brightness, brightness))
            strip.show()
            time.sleep(0.2)

            strip.set_all_pixels(Color(0, 0, 0))
            strip.show()
            time.sleep(0.2)
        print("Welcome animation completed.")
    except Exception as e:
        print("Welcome animation error:", e)

def apply_command(cmd):
    global led_enabled
    global current_speed_pwm

    stop_all()

    if cmd == "forward":
        lgpio.tx_pwm(h, AIN2, 1000, current_speed_pwm)
        lgpio.gpio_write(h, AIN1, 0)
        lgpio.tx_pwm(h, BIN2, 1000, current_speed_pwm)
        lgpio.gpio_write(h, BIN1, 0)
        print(f"Moving forward at {current_speed_pwm}% speed.")

    elif cmd == "backward":
        lgpio.tx_pwm(h, AIN1, 1000, current_speed_pwm)
        lgpio.gpio_write(h, AIN2, 0)
        lgpio.tx_pwm(h, BIN1, 1000, current_speed_pwm)
        lgpio.gpio_write(h, BIN2, 0)
        print(f"Moving backward at {current_speed_pwm}% speed.")

    elif cmd == "left":
        lgpio.tx_pwm(h, AIN1, 1000, current_speed_pwm)
        lgpio.gpio_write(h, AIN2, 0)
        lgpio.tx_pwm(h, BIN2, 1000, current_speed_pwm)
        lgpio.gpio_write(h, BIN1, 0)
        time.sleep(0.3)
        stop_all()
        print(f"Turning left at {current_speed_pwm}% speed.")

    elif cmd == "right":
        lgpio.tx_pwm(h, AIN2, 1000, current_speed_pwm)
        lgpio.gpio_write(h, AIN1, 0)
        lgpio.tx_pwm(h, BIN1, 1000, current_speed_pwm)
        lgpio.gpio_write(h, BIN2, 0)
        time.sleep(0.3)
        stop_all()
        print(f"Turning right at {current_speed_pwm}% speed.")

    elif cmd == "gear1":
        current_speed_pwm = 30
        print("Gear 1 selected: 30% speed.")

    elif cmd == "gear2":
        current_speed_pwm = 40
        print("Gear 2 selected: 40% speed.")

    elif cmd == "gear3":
        current_speed_pwm = 50
        print("Gear 3 selected: 50% speed.")

    elif cmd == "led_ready":
        print("LED system is ready.")
        led_enabled = True

    elif cmd == "vehicle_startup":
        print("Vehicle startup detected. Playing welcome animation.")
        welcome_animation()

    elif cmd == "stop":
        stop_all()
        print("Vehicle stopped.")

    elif cmd.startswith("led_"):
        if not led_enabled:
            print("LED command ignored, LEDs not ready.")
            return
        try:
            _, color, level = cmd.split("_")
            r, g, b = COLORS.get(color, (0, 0, 0))
            brightness = LEVELS.get(level, 0)
            strip.set_all_pixels(Color(r * brightness, g * brightness, b * brightness))
            strip.show()
            print(f"LED set to {color} at {level} brightness.")
        except Exception as e:
            print("LED command error:", e)


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

def safe_post(url, data):
    try:
        response = requests.post(url, json=data, timeout=5)
        print("POST response:", response.status_code, response.text)
    except Exception as e:
        print("POST error:", e)

def safe_get(url):
    try:
        response = requests.get(url, timeout=5)
        return response
    except Exception as e:
        print("GET error:", e)
        return None

def play_text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='tr')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        pygame.mixer.music.load(mp3_fp, 'mp3')
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            continue
    except Exception as e:
        print("Text-to-Speech error:", e)

def listen_for_speak():
    while True:
        try:
            speak_response = safe_get("https://robot-api-57ew.onrender.com/get-speak")
            if speak_response and speak_response.status_code == 200:
                speak_data = speak_response.json()
                text = speak_data.get("text", "")
                if text:
                    print(f"Speaking: {text}")
                    threading.Thread(target=play_text_to_speech, args=(text,)).start()
        except Exception as e:
            print("Speak listen error:", e)

        time.sleep(1)

print("Listener started...")
vehicle_on = False

threading.Thread(target=listen_for_speak, daemon=True).start()

while True:
    try:
        status = safe_get("https://robot-api-57ew.onrender.com/get-vehicle-status")
        if status and status.status_code == 200:
            vehicle_on = status.json().get("vehicle_on", False)
        else:
            vehicle_on = False

        if vehicle_on:
            command_response = safe_get("https://robot-api-57ew.onrender.com/get-command")
            if command_response and command_response.status_code == 200:
                cmd = command_response.json().get("command")
                if cmd:
                    print("Command received:", cmd)
                    apply_command(cmd)
        else:
            stop_all()

        dist = measure_distance()
        light = read_light()
        print(f"Sending: Distance={dist} cm, Light={light}")

        safe_post("https://robot-api-57ew.onrender.com/set-status", {
            "distance": dist,
            "light": light
        })

    except Exception as e:
        print("Loop error:", e)

    time.sleep(0.5)
