#http://localhost:5000/
from flask import Flask, request, render_template
from gtts import gTTS
import pygame
import io

app = Flask(__name__)

def text_to_speech(text):
    tts = gTTS(text=text, lang="tr")
    
    # Bellekte ses dosyası oluştur
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    # Pygame ile sesi çal
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp, 'mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_text = request.form["text"]
        text_to_speech(user_text)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
