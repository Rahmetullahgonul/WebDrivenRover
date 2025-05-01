import lgpio
from flask import Flask, render_template_string

app = Flask(__name__)

ldr_pin = 5  # GPIO5 kullaniliyor
h = lgpio.gpiochip_open(0)

pin_claimed = False  # Bu flag ile pin sadece bir kez acilacak

html = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="2">
    <title>LDR Sensor Status</title>
    <style>
        body{font-family:Arial, sans-serif; text-align:center; margin-top:50px;}
        .status{font-size:2em;}
    </style>
</head>
<body>
    <h1>LDR Sensor Status</h1>
    <div class="status">{{ status }}</div>
</body>
</html>
"""

@app.route('/')
def index():
    global pin_claimed
    if not pin_claimed:
        try:
            lgpio.gpio_claim_input(h, ldr_pin)
            pin_claimed = True
        except:
            pass  # Zaten acik olabilir

    value = lgpio.gpio_read(h, ldr_pin)
    if value == 0:
        status = "Environment is Bright!"
    else:
        status = "Environment is Dark!"

    return render_template_string(html, status=status)

if __name__ == '__main__':
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        lgpio.gpiochip_close(h)
        print("Program terminated.")
