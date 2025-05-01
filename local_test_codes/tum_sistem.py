from flask import Flask, render_template_string, request, redirect
from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
import lgpio
import time
import threading

app = Flask(__name__)

# ----- Motor Control Setup -----
AIN1 = 12
AIN2 = 13
BIN1 = 20
BIN2 = 21

h = lgpio.gpiochip_open(0)
for pin in [AIN1, AIN2, BIN1, BIN2]:
    lgpio.gpio_claim_output(h, pin)

current_speed = 50
current_action = "Stopped"

# ----- LED Control Setup -----
strip = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=8).get_strip()
COLORS = {
    "red": (1, 0, 0),
    "green": (0, 1, 0),
    "blue": (0, 0, 1)
}
LEVELS = {
    "low": 50,
    "medium": 125,
    "high": 255
}

# ----- Ultrasonic Sensor Setup -----
TRIG = 23
ECHO = 24
lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)
distance_cm = 0

# ----- LDR Sensor Setup -----
ldr_pin = 5
light_status = "Unknown"
ldr_claimed = False

# ----- Sensor Functions -----
def measure_distance():
    global distance_cm
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
            distance_cm = -1
            return

    end_time = time.time()
    timeout = end_time + 0.04
    while lgpio.gpio_read(h, ECHO) == 1:
        end_time = time.time()
        if end_time > timeout:
            distance_cm = -1
            return

    pulse_duration = end_time - start_time
    distance_cm = round(pulse_duration * 17150, 2)

def read_light():
    global light_status, ldr_claimed
    if not ldr_claimed:
        try:
            lgpio.gpio_claim_input(h, ldr_pin)
            ldr_claimed = True
        except:
            pass
    value = lgpio.gpio_read(h, ldr_pin)
    light_status = "Bright" if value == 0 else "Dark"

# ----- Background Thread for Sensors -----
def update_sensors():
    while True:
        measure_distance()
        read_light()
        time.sleep(1)

threading.Thread(target=update_sensors, daemon=True).start()

# ----- Utility Functions -----
def stop_all():
    for pin in [AIN1, AIN2, BIN1, BIN2]:
        lgpio.tx_pwm(h, pin, 1000, 0)

# ----- Routes -----
@app.route("/", methods=["GET", "POST"])
def index():
    global current_speed, current_action

    if request.method == "POST":
        if "speed" in request.form:
            current_speed = int(request.form["speed"])

        action = request.form.get("action")
        duty = current_speed

        stop_all()

        if action == "forward":
            lgpio.tx_pwm(h, AIN1, 1000, duty)
            lgpio.gpio_write(h, AIN2, 0)
            lgpio.tx_pwm(h, BIN1, 1000, duty)
            lgpio.gpio_write(h, BIN2, 0)
            current_action = "Forward"

        elif action == "backward":
            lgpio.tx_pwm(h, AIN2, 1000, duty)
            lgpio.gpio_write(h, AIN1, 0)
            lgpio.tx_pwm(h, BIN2, 1000, duty)
            lgpio.gpio_write(h, BIN1, 0)
            current_action = "Backward"

        elif action == "left":
            lgpio.tx_pwm(h, AIN1, 1000, duty)
            lgpio.gpio_write(h, AIN2, 0)
            lgpio.tx_pwm(h, BIN2, 1000, duty)
            lgpio.gpio_write(h, BIN1, 0)
            time.sleep(0.3)
            stop_all()
            current_action = "Left Turn"

        elif action == "right":
            lgpio.tx_pwm(h, AIN2, 1000, duty)
            lgpio.gpio_write(h, AIN1, 0)
            lgpio.tx_pwm(h, BIN1, 1000, duty)
            lgpio.gpio_write(h, BIN2, 0)
            time.sleep(0.3)
            stop_all()
            current_action = "Right Turn"

        elif action == "stop":
            stop_all()
            current_action = "Stopped"

        elif action and action.startswith("led_"):
            color, level = action.split("_")[1:]
            r_base, g_base, b_base = COLORS.get(color, (0, 0, 0))
            brightness = LEVELS.get(level, 0)
            r = r_base * brightness
            g = g_base * brightness
            b = b_base * brightness
            strip.set_all_pixels(Color(r, g, b))
            strip.show()
            current_action = f"LED {color} {level}"

        elif action == "led_off":
            strip.set_all_pixels(Color(0, 0, 0))
            strip.show()
            current_action = "LED Off"

    return render_template_string(html_motor, speed=current_speed, action=current_action, distance=distance_cm, light=light_status)

# ----- HTML -----
html_motor = """
<!DOCTYPE html>
<html>
<head>
    <title>Robot Car Control Panel</title>
    <meta http-equiv="refresh" content="2">
</head>
<body>
    <h1>Robot Car Control</h1>
    <form method="POST">
        <label for="speed">Speed (%20 - %100):</label>
        <input type="range" id="speed" name="speed" min="20" max="100" value="{{ speed }}" oninput="this.nextElementSibling.value = this.value">
        <output>{{ speed }}</output>%
        <br><br>
        <button name="action" value="forward">Backward</button>
        <button name="action" value="backward">Forward</button>
        <button name="action" value="left">Left</button>
        <button name="action" value="right">Right</button>
        <button name="action" value="stop">Stop</button>
    </form>

    <h2>LED Control</h2>
    <form method="POST">
        {% for color in ['red', 'green', 'blue'] %}
            <h3>{{ color.capitalize() }}</h3>
            {% for level in ['low', 'medium', 'high'] %}
                <button name="action" value="led_{{ color }}_{{ level }}">{{ level.capitalize() }}</button>
            {% endfor %}
        {% endfor %}
        <br>
        <button name="action" value="led_off" style="background-color:black; color:white;">Off</button>
    </form>

    <h2>Ultrasonic Sensor</h2>
    <p>Distance: <strong>{{ distance }} cm</strong></p>

    <h2>LDR Sensor</h2>
    <p>Environment: <strong>{{ light }}</strong></p>

    <p>Current action: <strong>{{ action }}</strong></p>
    <p>Current speed: <strong>{{ speed }}%</strong></p>
</body>
</html>
"""

try:
    app.run(host="0.0.0.0", port=5000)
except KeyboardInterrupt:
    stop_all()
    lgpio.gpiochip_close(h)
