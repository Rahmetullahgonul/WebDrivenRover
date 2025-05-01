from flask import Flask, render_template_string, request
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# GPIO setup
GPIO.setmode(GPIO.BCM)
IN1 = 17
IN2 = 27
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

# Simple HTML UI
html = """
<!doctype html>
<title>Motor Control</title>
<h1>Raspberry Pi Motor Control</h1>
<form method="POST">
    <button name="action" value="forward">Forward</button>
    <button name="action" value="backward">Backward</button>
    <button name="action" value="stop">Stop</button>
</form>
<p>Last command: {{ command }}</p>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    command = "No command yet"
    if request.method == "POST":
        action = request.form["action"]
        if action == "forward":
            forward()
            command = "Forward"
        elif action == "backward":
            backward()
            command = "Backward"
        elif action == "stop":
            stop()
            command = "Stop"
    return render_template_string(html, command=command)

try:
    app.run(host="0.0.0.0", port=5000)

except KeyboardInterrupt:
    GPIO.cleanup()
