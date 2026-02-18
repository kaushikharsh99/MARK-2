import subprocess
import os
import platform
import time
import requests
import signal
from ..base_module_adapter import BaseModuleAdapter

class BitNetAdapter(BaseModuleAdapter):
    def __init__(self):
        self.server_process = None
        self.port = 5000
        self.status = "Idle"
        self.model_name = "BitNet b1.58 2B"

    def load(self, config):
        self.status = "Loading"
        self.unload()
        
        root_dir = os.path.join(os.getcwd(), "BitNet")
        server_script = os.path.join(root_dir, "run_inference_server.py")
        
        # Determine the correct python executable (prefer the bitnet_env)
        python_exe = "python"
        env_path = os.path.join(root_dir, "bitnet_env", "bin", "python")
        if platform.system() == "Windows":
            env_path = os.path.join(root_dir, "bitnet_env", "Scripts", "python.exe")
        
        if os.path.exists(env_path):
            python_exe = env_path
            print(f"🐍 Using BitNet environment python: {python_exe}")

        # Set port to 5000 as per the user's command example
        self.port = 5000
        
        model_name = config.get("model")
        model_path = ""
        
        if model_name and not os.path.isabs(model_name):
            # Try to find the model file in the BitNet models directory
            check_path = os.path.join(root_dir, "models", model_name)
            if os.path.exists(check_path):
                model_path = os.path.join("models", model_name)
            else:
                # Fallback to searching
                found = False
                for root, dirs, files in os.walk(os.path.join(root_dir, "models")):
                    if model_name in files:
                        model_path = os.path.relpath(os.path.join(root, model_name), root_dir)
                        found = True
                        break
                if not found:
                    model_path = "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
        else:
            model_path = model_name or "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"

        # BitNet is locked to these settings for stability
        command = [
            python_exe, server_script,
            "-m", model_path,
            "-t", "2", # Locked to 2 threads
            "-c", "1024", # Lower context size for stability
            "-n", "512", # Prediction limit
            "--port", str(self.port),
            "--host", "127.0.0.1",
            "--temperature", "0.8" # Preferred humor temperature
        ]
        
        system_prompt = config.get("system_prompt") or "You are a humorous AI assistant. Respond in exactly one line."
        command.extend(["-p", system_prompt])
        
        print(f"🚀 Launching BitNet server: {' '.join(command)}")
        
        # Log to a temp file outside BitNet
        log_path = os.path.join(os.getcwd(), "bitnet_server.log")
        log_file = open(log_path, "w")
        
        # Verify binary exists to avoid silent failures
        binary_path = os.path.join(root_dir, "build", "bin", "llama-server")
        if not os.path.exists(binary_path):
            print(f"⚠️ Warning: BitNet binary not found at {binary_path}. The server script might fail.")

        self.server_process = subprocess.Popen(
            command,
            stdout=log_file,
            stderr=log_file,
            cwd=root_dir,
            preexec_fn=os.setsid if platform.system() == "Linux" else None,
        )
        
        # Poll health endpoint - give it more time (60s)
        for i in range(60):
            try:
                res = requests.get(f"http://127.0.0.1:{self.port}/health", timeout=2)
                if res.status_code == 200:
                    print(f"✅ BitNet server is up on port {self.port}")
                    self.status = "Running"
                    return True
            except: pass
            if i % 5 == 0:
                print(f"⏳ Waiting for BitNet server... ({i}s)")
            time.sleep(1)
        
        self.status = "Error: Startup Timeout"
        return False

    def generate(self, prompt, params):
        # BitNet llama-server usually uses /completion or /v1/chat/completions
        endpoints = ["/completion", "/v1/chat/completions", "/v1/completions"]
        
        data_legacy = {
            "prompt": prompt,
            "n_predict": params.get("max_tokens", 128),
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 1.0),
            "repeat_penalty": 1.0 + params.get("frequency_penalty", 0.0),
            "stop": ["User:", "\n\n", "Jarvis:"]
        }
        
        data_v1 = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": params.get("max_tokens", 128),
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 1.0),
            "presence_penalty": params.get("frequency_penalty", 0.0)
        }

        for endpoint in endpoints:
            url = f"http://127.0.0.1:{self.port}{endpoint}"
            payload = data_v1 if "v1" in endpoint else data_legacy
            
            try:
                print(f"🔍 Attempting generation at {url}...")
                response = requests.post(url, json=payload, timeout=60)
                
                if response.status_code == 200:
                    res_json = response.json()
                    if "content" in res_json:
                        return res_json["content"].strip()
                    if "choices" in res_json:
                        choice = res_json["choices"][0]
                        if "message" in choice:
                            return choice["message"]["content"].strip()
                        if "text" in choice:
                            return choice["text"].strip()
                    return str(res_json)
                
                print(f"⚠️ Endpoint {endpoint} returned {response.status_code}")
            except Exception as e:
                print(f"❌ Connection failed to {endpoint}: {e}")
                continue
        
        return "Error: All generation endpoints failed (Connection Refused or 404)"

    def unload(self):
        if self.server_process:
            try:
                print(f"🛑 Shutting down BitNet server on port {self.port}...")
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
