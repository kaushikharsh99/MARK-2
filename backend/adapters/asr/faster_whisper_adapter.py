import os
import subprocess
from ..base_module_adapter import BaseModuleAdapter

class FasterWhisperAdapter(BaseModuleAdapter):
    def __init__(self):
        self.model = None
        self.status = "Idle"
        self.model_name = "None"

    def load(self, config):
        self.status = "Loading"
        model_size = config.get("model", "base")
        device = "cuda" if config.get("gpu_layers", 0) > 0 else "cpu"
        
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(model_size, device=device, compute_type="float16" if device == "cuda" else "int8")
            self.model_name = model_size
            self.status = "Running"
            return True
        except Exception as e:
            self.status = f"Error: {str(e)}"
            return False

    def generate(self, audio_path, params):
        if not self.model: return "Error: Model not loaded"
        try:
            segments, info = self.model.transcribe(audio_path, beam_size=5)
            return " ".join([segment.text for segment in segments]).strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def unload(self):
        self.model = None
        self.status = "Idle"

    def get_status(self):
        return {"status": self.status, "model": self.model_name}
