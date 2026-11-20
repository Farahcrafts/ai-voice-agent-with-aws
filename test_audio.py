import pyaudio
import wave

# Paramètres
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "test_micro.wav"

p = pyaudio.PyAudio()

print("🎤 Enregistrement de 3 secondes... Parle !")
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("✅ Enregistrement terminé !")
stream.stop_stream()
stream.close()
p.terminate()

# On sauvegarde pour écouter
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
print(f"Écoute le fichier {WAVE_OUTPUT_FILENAME} pour vérifier !")