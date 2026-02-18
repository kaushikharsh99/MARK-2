import os
import wave
import json
from ..base_module_adapter import BaseModuleAdapter

class VoskAdapter(BaseModuleAdapter):
    def __init__(self):
        self.model = None
        self.status = "Idle"
        self.model_name = "None"

    def load(self, config):
        self.status = "Loading"
        model_name = config.get("model")
        if not model_name:
            self.status = "Error: No model specified"
            return False
            
        try:
            from vosk import Model, KaldiRecognizer
            model_path = os.path.join("vosk_models", model_name)
            if not os.path.exists(model_path):
                self.status = f"Error: {model_name} not found"
                return False
                
            self.model = Model(model_path)
            self.model_name = model_name
            self.status = "Running"
            return True
        except Exception as e:
            self.status = f"Error: {str(e)}"
            return False

    def generate(self, audio_path, params):
        if not self.model: return "Error: Model not loaded"
        try:
            from vosk import KaldiRecognizer
            wf = wave.open(audio_path, "rb")
            rec = KaldiRecognizer(self.model, wf.getframerate())
            
            result = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    result += res.get("text", "") + " "
            
            res = json.loads(rec.FinalResult())
            result += res.get("text", "")
            return result.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def unload(self):
        self.model = None
        self.status = "Idle"

    def get_status(self):
        return {"status": self.status, "model": self.model_name}
