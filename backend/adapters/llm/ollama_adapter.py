import requests
import json
import subprocess
import time
import os
import signal
import platform
from ..base_module_adapter import BaseModuleAdapter

class OllamaAdapter(BaseModuleAdapter):
    def __init__(self):
        self.port = 11434
        self.status = "Idle"
        self.model_name = "None"
        self.server_process = None

    def load(self, config):
        self.model_name = config.get("model", "llama3.2:3b")
        
        # 1. Check if Ollama is already running
        try:
            res = requests.get(f"http://127.0.0.1:{self.port}/api/tags", timeout=2)
            if res.status_code == 200:
                self.status = "Running"
                return True
        except:
            pass
            
        # 2. Try to start Ollama serve
        self.status = "Starting Server"
        try:
            self.server_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid if platform.system() == "Linux" else None,
            )
            
            # Wait for server to be ready
            for _ in range(10):
                try:
                    res = requests.get(f"http://127.0.0.1:{self.port}/api/tags", timeout=1)
                    if res.status_code == 200:
                        self.status = "Running"
                        return True
                except:
                    pass
                time.sleep(1)
        except Exception as e:
            self.status = f"Error: {str(e)}"
            return False
            
        self.status = "Error: Timeout starting Ollama"
        return False

    def generate(self, prompt, params):
        url = f"http://127.0.0.1:{self.port}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": params.get("temperature", 0.7),
                "num_predict": params.get("max_tokens", 128),
                "top_p": params.get("top_p", 1.0),
                "repeat_penalty": 1.0 + params.get("frequency_penalty", 0.0),
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except Exception as e:
            return f"Error: {str(e)}"
        
        return "Error: Generation failed"

    def unload(self):
        if self.server_process:
            try:
                if platform.system() == "Windows":
                    self.server_process.terminate()
                else:
                    os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
            except:
                pass
            self.server_process = None
        self.status = "Idle"

    def get_status(self):
        return {
            "status": self.status,
            "model": self.model_name,
            "port": self.port
        }
