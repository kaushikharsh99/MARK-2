import os
import subprocess
import tempfile
from ..base_module_adapter import BaseModuleAdapter

class CoquiTTSAdapter(BaseModuleAdapter):
    def __init__(self):
        self.tts = None
        self.status = "Idle"
        self.model_name = "None"

    def load(self, config):
        self.status = "Loading"
        model_name = config.get("model", "tts_models/en/ljspeech/vits")
        
        try:
            from TTS.api import TTS
            self.tts = TTS(model_name=model_name, progress_bar=False)
            self.model_name = model_name
            self.status = "Running"
            return True
        except Exception as e:
            self.status = f"Error: {str(e)}"
            return False

    def generate(self, text, params):
        if not self.tts: return None
        output_wav = params.get("output_path")
        if not output_wav: return None
        
        try:
            self.tts.tts_to_file(text=text, file_path=output_wav)
            return output_wav
        except Exception as e:
            print(f"Coqui TTS Error: {e}")
            return None

    def unload(self):
        self.tts = None
        self.status = "Idle"

    def get_status(self):
        return {"status": self.status, "model": self.model_name}
