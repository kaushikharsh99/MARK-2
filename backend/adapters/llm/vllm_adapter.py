import subprocess
import os
import platform
import time
import requests
import signal
from ..base_module_adapter import BaseModuleAdapter

class VLLMAdapter(BaseModuleAdapter):
    def __init__(self):
        self.server_process = None
        self.port = 8081
        self.status = "Idle"
        self.model_name = "None"

    def load(self, config):
        self.status = "Loading"
        self.unload()
        
        model_name = config.get("model")
        if not model_name:
            self.status = "Error: No model specified"
            return False
            
        self.model_name = model_name

        # Command to start vLLM OpenAI-compatible server
        command = [
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", model_name,
            "--port", str(self.port),
            "--host", "127.0.0.1"
        ]
        
        # Add GPU config if present
        gpu_memory_utilization = config.get("gpu_memory_utilization", 0.9)
        command.extend(["--gpu-memory-utilization", str(gpu_memory_utilization)])
        
        self.server_process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid if platform.system() == "Linux" else None,
        )
        
        # Poll health endpoint (vLLM has /health)
        for _ in range(60): # vLLM can take longer to load models
            try:
                res = requests.get(f"http://127.0.0.1:{self.port}/health", timeout=2)
                if res.status_code == 200:
                    self.status = "Running"
                    return True
            except: pass
            time.sleep(2)
        
        self.status = "Error: Startup Timeout"
        return False

    def generate(self, prompt, params):
        url = f"http://127.0.0.1:{self.port}/v1/completions"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": params.get("max_tokens", 128),
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 1.0),
            "frequency_penalty": params.get("frequency_penalty", 0.0),
            "stop": ["User:", "\n\n", "Jarvis:"]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                res_json = response.json()
                if "choices" in res_json and len(res_json["choices"]) > 0:
                    return res_json["choices"][0].get("text", "").strip()
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
            except: pass
            self.server_process = None
        self.status = "Idle"

    def get_status(self):
        return {
            "status": self.status,
            "model": self.model_name,
            "port": self.port
        }
