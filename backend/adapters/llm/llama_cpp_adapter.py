import subprocess
import os
import platform
import time
import requests
import signal
import shutil
from ..base_module_adapter import BaseModuleAdapter

class LlamaCppAdapter(BaseModuleAdapter):
    def __init__(self):
        self.server_process = None
        self.port = 8080
        self.status = "Idle"
        self.model_name = "None"

    def load(self, config):
        self.status = "Loading"
        self.unload()
        
        # Search for llama-server in PATH and local build directory
        search_paths = [
            shutil.which("llama-server"),
            shutil.which("llama-cli"),
            shutil.which("main"),
            "llama.cpp/build/bin/llama-server",
            "llama.cpp/build/bin/llama-cli",
            "llama.cpp/main"
        ]
        
        server_path = next((p for p in search_paths if p and os.path.exists(p) or (p and shutil.which(p))), None)
        
        if not server_path:
            self.status = "Error: llama-server not found"
            return False

        model_name = config.get("model")
        model_path = model_name
        
        if model_name and not os.path.isabs(model_name):
            # Check common locations
            paths_to_check = ["models", "llama.cpp/models", "."]
            for p in paths_to_check:
                check_path = os.path.join(p, model_name)
                if os.path.exists(check_path):
                    model_path = check_path
                    break

        if not model_path or not os.path.exists(model_path):
            self.status = "Error: Model not found"
            return False

        self.model_name = os.path.basename(model_path)

        command = [
            server_path,
            "-m", model_path,
            "-t", str(config.get("cpu_threads", 4)),
            "-c", str(config.get("context_window", 2048)),
            "-n", str(config.get("max_tokens", 2048)),
            "--port", str(self.port),
            "--host", "127.0.0.1",
            "-ngl", str(config.get("gpu_layers", 0))
        ]
        
        self.server_process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid if platform.system() == "Linux" else None,
        )
        
        for _ in range(30):
            try:
                res = requests.get(f"http://127.0.0.1:{self.port}/health", timeout=2)
                if res.status_code == 200:
                    self.status = "Running"
                    return True
            except: pass
            time.sleep(1)
        
        self.status = "Error: Startup Timeout"
        return False

    def generate(self, prompt, params):
        url = f"http://127.0.0.1:{self.port}/completion"
        payload = {
            "prompt": prompt,
            "n_predict": params.get("max_tokens", 128),
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 1.0),
            "repeat_penalty": 1.0 + params.get("frequency_penalty", 0.0),
            "stop": ["User:", "\n\n", "Jarvis:"]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get("content", "").strip()
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
