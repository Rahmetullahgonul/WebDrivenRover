'''
from gtts import gTTS
import pygame
import io

def text_to_speech(text, language='tr'):
    tts = gTTS(text=text, lang=language)
    
    # Ses dosyasını hafızaya (belleğe) kaydet
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    
    # Bellekten okumak için başa sar
    mp3_fp.seek(0)

    # Pygame ile sesi çal
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp, 'mp3')
    pygame.mixer.music.play()

    # Sesin tamamlanmasını bekle
    while pygame.mixer.music.get_busy():
        continue

if __name__ == "__main__":
    metin = input("Lütfen bir metin girin: ")
    text_to_speech(metin)
'''
#--------------------------------------------------------------------------------------------
'''
#raspberry de calisan kod:
from gtts import gTTS
import pygame
import io

def text_to_speech(text, language='tr'):
    tts = gTTS(text=text, lang=language)

    # Create audio in memory
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    # Play with pygame
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_fp, 'mp3')
    pygame.mixer.music.play()

    # Wait until playback is done
    while pygame.mixer.music.get_busy():
        continue

if __name__ == "__main__":
    text = input("Enter text: ")
    text_to_speech(text)
'''
#----------------------------------------------------------------------------------------------------
'''
#internetsiz ve raspberryi de calisan kod 
import os

def text_to_speech(text):
    os.system(f'espeak "{text}" -vtr')

if __name__ == "__main__":
    text = input("Enter text: ")
    text_to_speech(text)
'''