import pyaudio
import asyncio

# --- 1. LE FAUX CERVEAU (Remplace BedrockStreamManager) ---
class FakeBrain:
    def __init__(self):
        # C'est la file d'attente où le son arrive
        self.audio_output_queue = asyncio.Queue()
    
    def add_audio_chunk(self, audio_data):
        # Au lieu d'envoyer à AWS, on renvoie le son tel quel dans la file de sortie
        self.audio_output_queue.put_nowait(audio_data)

# --- 2. LA VERSION SIMPLIFIÉE DE AUDIOSTREAMER ---
class MiniAudioStreamer:
    def __init__(self, brain):
        self.brain = brain
        self.is_streaming = False
        self.loop = asyncio.get_event_loop()
        
        self.p = pyaudio.PyAudio()
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024

        # On ouvre le micro (avec un callback)
        self.input_stream = self.p.open(
            format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, 
            input=True, frames_per_buffer=self.CHUNK, 
            stream_callback=self.input_callback # <--- Le fameux callback
        )
        
        # On ouvre les haut-parleurs
        self.output_stream = self.p.open(
            format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, 
            output=True, frames_per_buffer=self.CHUNK
        )

    # --- LA FONCTION INPUT_CALLBACK ---
    def input_callback(self, in_data, frame_count, time_info, status):
        if self.is_streaming:
            # Dès qu'on capte du son, on l'envoie à la fonction process_input
            asyncio.run_coroutine_threadsafe(self.process_input(in_data), self.loop)
        return (None, pyaudio.paContinue)

    async def process_input(self, data):
        # On donne le son au cerveau
        self.brain.add_audio_chunk(data)

    # --- LA FONCTION PLAY_OUTPUT ---
    async def play_output(self):
        while self.is_streaming:
            try:
                # On attend de recevoir du son du cerveau (timeout de 0.1s)
                audio_data = await asyncio.wait_for(self.brain.audio_output_queue.get(), timeout=0.1)
                
                if audio_data:
                    # On joue le son dans les haut-parleurs
                    await self.loop.run_in_executor(None, self.output_stream.write, audio_data)
            except asyncio.TimeoutError:
                # Si pas de son pendant 0.1s, on boucle et on réécoute
                pass

    # --- START ET STOP ---
    async def run(self):
        self.is_streaming = True
        self.input_stream.start_stream()
        
        # On lance la boucle d'écoute des réponses en arrière-plan
        output_task = asyncio.create_task(self.play_output())
        
        print("🎤 Parle dans ton micro... (Tu vas t'entendre en écho)")
        print("Appuie sur 'Entrée' pour arrêter.")
        
        # Attend que tu appuies sur Entrée
        await self.loop.run_in_executor(None, input)
        
        # Nettoyage
        self.is_streaming = False
        output_task.cancel()
        self.input_stream.close()
        self.output_stream.close()
        self.p.terminate()
        print("✅ Terminé !")

# --- LANCEMENT ---
async def main():
    brain = FakeBrain()
    streamer = MiniAudioStreamer(brain)
    await streamer.run()

if __name__ == "__main__":
    asyncio.run(main())