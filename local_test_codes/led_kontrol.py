# -*- coding: utf-8 -*-
from flask import Flask, request, redirect
from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
import threading

app = Flask(__name__)

# LED ayarÃ½
strip = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=8).get_strip()

# Renk ve parlaklÃ½k eÃ¾lemeleri
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

# Ana sayfa ve butonlar
@app.route('/')
def index():
    html = "<h1>LED Renk ve Parlaklik Kontrol</h1>"
    for color in COLORS:
        html += f"<h2>{color.capitalize()}</h2>"
        for level in LEVELS:
            html += f'''
            <form action="/set" method="POST" style="display:inline;">
                <input type="hidden" name="color" value="{color}">
                <input type="hidden" name="level" value="{level}">
                <button>{level.capitalize()}</button>
            </form>
            '''
    # LED'leri kapat butonu
    html += '''
    <h2>LED'leri Kapat</h2>
    <form action="/off" method="POST">
        <button style="background-color:black; color:white;">Kapat</button>
    </form>
    '''
    return html

# Renk/parlaklÃ½k ayarÃ½
@app.route('/set', methods=['POST'])
def set_color():
    color = request.form.get("color")
    level = request.form.get("level")

    r_base, g_base, b_base = COLORS.get(color, (0, 0, 0))
    brightness = LEVELS.get(level, 0)

    r = r_base * brightness
    g = g_base * brightness
    b = b_base * brightness

    strip.set_all_pixels(Color(r, g, b))
    strip.show()

    return redirect('/')

# TÃ¼m LED'leri kapat
@app.route('/off', methods=['POST'])
def turn_off():
    strip.set_all_pixels(Color(0, 0, 0))
    strip.show()
    return redirect('/')


def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Flask'i ayrÃ½ thread'de baÃ¾lat
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
