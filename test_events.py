import json
import asyncio
import uuid

# --- 1. ON CRÉE UNE VERSION SIMPLIFIÉE DE LA CLASSE ---
# (J'ai enlevé les imports AWS et les vraies connexions)
class FakeBedrockStreamManager:
    def __init__(self):
        self.prompt_name = str(uuid.uuid4())
        self.content_name = str(uuid.uuid4())
        self.audio_content_name = str(uuid.uuid4())
        
        # On simule quelques events
        self.START_SESSION_EVENT = '{"event": {"sessionStart": {}}}'
        self.TEXT_CONTENT_START_EVENT = '{"event": {"contentStart": {"promptName": "%s", "contentName": "%s", "role": "%s"}}}'
        self.TEXT_INPUT_EVENT = '{"event": {"textInput": {"content": "%s"}}}'
        self.CONTENT_END_EVENT = '{"event": {"contentEnd": {"promptName": "%s"}}}'
        self.AUDIO_EVENT_TEMPLATE = '{"event": {"audioInput": {"promptName": "%s", "content": "%s"}}}'

    async def send_raw_event(self, event_json):
        """C'est ici qu'on simule l'envoi à AWS (on l'affiche juste)"""
        print(f"📤 ENVOI À AWS : {event_json[:100]}...") # On coupe pour faire court
        await asyncio.sleep(0.1)

    async def initialize_stream(self):
        """La méthode de démarrage"""
        print("🚀 Initialisation du Stream...")
        default_system_prompt = "Tu es un assistant d'hotel."
        
        # On prépare les events (comme dans le vrai code)
        text_content_start = self.TEXT_CONTENT_START_EVENT % (self.prompt_name, self.content_name, "SYSTEM")
        text_content = self.TEXT_INPUT_EVENT % (default_system_prompt)
        text_content_end = self.CONTENT_END_EVENT % (self.prompt_name)
        
        init_events = [
            self.START_SESSION_EVENT,
            text_content_start,
            text_content,
            text_content_end
        ]
        
        for event in init_events:
            await self.send_raw_event(event)

    async def simulate_audio_input(self):
        """On simule quelqu'un qui parle au micro"""
        print("\n🎤 L'utilisateur commence à parler...")
        faux_son_base64 = "ABC123XYZ" # Du faux son
        audio_event = self.AUDIO_EVENT_TEMPLATE % (self.prompt_name, faux_son_base64)
        await self.send_raw_event(audio_event)

# --- 2. ON LANCE LE TEST ---
async def main():
    manager = FakeBedrockStreamManager()
    
    # 1. On démarre (ça envoie le Start, le texte, le End)
    await manager.initialize_stream()
    
    # 2. On simule un mot prononcé au micro
    await manager.simulate_audio_input()

asyncio.run(main())