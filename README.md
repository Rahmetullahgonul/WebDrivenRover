# Web Driven Rover

This project presents a complete real-time control system for a two-motor robotic vehicle powered by a Raspberry Pi 5. The system integrates motor drivers, WS2812 RGB LEDs, an ultrasonic distance sensor, and an LDR light sensor all accessible and controllable through a web interface hosted on a custom domain. A lightweight Flask-based API, deployed via Render.com, enables seamless, low-latency communication between the user and the vehicle, allowing full remote operation over the internet.


## Features
The system offers a modular and responsive architecture for remote vehicle control, combining real-time hardware interaction with a lightweight web-based interface.
* Real-time web interface hosted on a custom domain for full vehicle control.
* Dual motor control using PWM via Raspberry Pi GPIO.
* WS2812 RGB LED control with adjustable brightness and color.
* Ultrasonic distance measurement integrated with live data updates.
* LDR sensor integration for ambient light detection.
* Multithreaded architecture for concurrent sensor monitoring.
* Flask-based backend API deployed on Render.com
* Conditional control logic for system safety (e.g., LEDs only work when vehicle is active).
 * Lightweight HTML interface using POST requests for all commands.

## Installation
### 1. Clone the repository 
```bash 
git clone https://github.com/Rahmetullahgonul/WebDrivenRover.git
cd WebDrivenRover
```
### 2. Install system dependencies (Raspberry Pi 5)
Ensure lgpio and required Python libraries are installed:
```bash 
sudo apt update
sudo apt install python3-pip python3-lgpio
pip3 install flask rpi_ws281x
```
Note: lgpio is required for GPIO-based motor and sensor control. The WS2812 LED strip requires SPI interface.
### 3. Enable SPI (for WS2812 LED control)
Enable SPI via Raspberry Pi configuration:
```bash 
sudo raspi-config
# Navigate to Interface Options → SPI → Enable
```
### 4. Run the local Flask server (for testing)
```bash 
cd local_test_codes
python3 local_sunucu.py
```
### 5. (Optional) Deploy the api/ folder to Render.com
* Create a new web service on Render.com
* Link it to this repository
* Set the build and start commands as follows:
```yaml 
Build Command: pip install -r requirements.txt
Start Command: python app.py
```
Make sure the render.yaml file is present for automatic deployment configuration.

## Project Structure
```bash 
WebDrivenRover/
├── api/                    # Flask API backend for remote deployment (Render.com)
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Dependencies for deployment
│   ├── render.yaml         # Render.com deployment configuration
│   └── README.md           # Backend documentation (optional)
│
├── local_test_codes/       # Local testing code for Raspberry Pi 5
│   ├── motor_kontrol.py    # Motor control script using lgpio
│   ├── led_kontrol.py      # WS2812 LED test code
│   ├── ultrasonik.py       # Ultrasonic sensor test
│   ├── ldr_kontrol.py      # LDR sensor reading script
│   ├── text_to_speech.py   # Optional audio feedback
│   ├── pi_listener.py      # Central script for integrated control
│   ├── local_sunucu.py     # Local Flask server for web control
│   └── templates/
│       └── index.html      # Web interface template
│
├── pi_code/                # Final integrated script for production use
│   └── pi_listener.py      # Unified motor, LED, and sensor control logic
│
├── web_page/               # Web interface source files (used with custom domain)
│   └── index.html          # HTML page for remote vehicle control
│
└── README.md               # Project documentation (this file)
```

## Usage
### 1. Local Test (on Raspberry Pi 5)
To run the system locally without internet access:
#### 1. Start the local Flask server
This will host the control panel interface:
```bash 
cd local_test_codes
python3 local_sunucu.py
```
#### 2. Start the integrated hardware controller
This script handles motor, LED, ultrasonic, and LDR control:
```bash 
python3 tum_sistem.py
```
#### 3. Access the control panel
Open a browser (on Pi or same network) and visit:
```bash 
http://<your-raspberry-pi-ip>:5000
```
From here, you can:
* Turn the vehicle on/off
* Control movement and LED settings
* Monitor distance and light sensor data in real time

### 2. Remote Control (via custom website and cloud API)
To control the vehicle remotely over the internet:
#### 1. Deploy the API backend to Render.com
* Connect your GitHub repo to Render
* Deploy the api/ folder as a Flask web service
* Ensure render.yaml is present and correct
#### 2. Start the Raspberry Pi listener
This script listens for incoming API requests and controls the vehicle:
```bash 
cd pi_code
python3 pi_listener.py
```
#### 3. Use the custom web interface
* Open your deployed web page hosted on your custom domain
* Control the vehicle via buttons (using POST requests to the API)
* Commands will be routed through Render to the Raspberry Pi

Important: Ensure your Raspberry Pi has internet access and can maintain a persistent connection to the Render-deployed API.


## Links

- **Live Control Panel**: [https://codeepicenter.com](https://codeepicenter.com)  
  Web-based interface to control the vehicle remotely.

- **API Deployment (Render)**: [https://render.com](https://render.com)  
  Hosted Flask backend for receiving and processing control commands.

## Wiring Diagram

The following GPIO pin assignments are used in this project:

| Component             | Signal         | Raspberry Pi GPIO Pin |
|----------------------|----------------|------------------------|
| Motor Driver - AIN1  | Motor A input  | GPIO 12                |
| Motor Driver - AIN2  | Motor A input  | GPIO 13                |
| Motor Driver - BIN1  | Motor B input  | GPIO 20                |
| Motor Driver - BIN2  | Motor B input  | GPIO 21                |
| Ultrasonic Sensor    | Trigger        | GPIO 23                |
| Ultrasonic Sensor    | Echo           | GPIO 24                |
| LDR Sensor           | Digital Output | GPIO 5                 |
| WS2812 RGB LED       | SPI (Data In)  | SPI0 MOSI (GPIO 10)    |

> Make sure to enable SPI via `sudo raspi-config` under Interface Options.



  
