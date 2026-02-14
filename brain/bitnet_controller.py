import subprocess
import os
import platform
import time
import requests
import signal

class BitNetController:
    def __init__(self, model_path=None, threads=4, port=8080):
        self.root_dir = os.path.join(os.getcwd(), "BitNet")
        self.build_dir = os.path.join(self.root_dir, "build")
        self.port = port
        self.threads = threads
        
        # Path to server binary
        if platform.system() == "Windows":
            self.server_path = os.path.join(self.build_dir, "bin", "Release", "llama-server.exe")
        else:
            self.server_path = os.path.join(self.build_dir, "bin", "llama-server")
            
        if model_path:
            self.model_path = model_path
        else:
            self.model_path = os.path.join(self.root_dir, "models", "BitNet-b1.58-2B-4T", "ggml-model-i2_s.gguf")
            
        self.server_process = None
        self.start_server()

    def start_server(self):
        """Starts the llama-server in the background."""
        print(f"🚀 Starting BitNet Server (CPU, {self.threads} threads)...")
        
        command = [
            self.server_path,
            "-m", self.model_path,
            "-t", str(self.threads),
            "-c", "2048",
            "--port", str(self.port),
            "--host", "127.0.0.1",
            "-ngl", "0"  # CPU only
        ]
        
        # Start the server and redirect output to null to keep console clean
        self.server_process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=self.root_dir,
            preexec_fn=os.setsid if platform.system() != "Windows" else None
        )
        
        # Wait for server to be ready
        print("⏳ Waiting for model to load into RAM...")
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"http://127.0.0.1:{self.port}/health")
                if response.status_code == 200:
                    print("✅ BitNet Loaded and Persistent.")
                    return
            except:
                pass
            time.sleep(1)
        print("❌ Server failed to start.")

    def generate(self, prompt, n_predict=128, temp=0.7):
        """Sends a request to the persistent server."""
        url = f"http://127.0.0.1:{self.port}/completion"
        data = {
            "prompt": prompt,
            "n_predict": n_predict,
            "temperature": temp,
            "stop": ["User:", "\n\n"]
        }
        
        try:
            response = requests.post(url, json=data, timeout=60)
            if response.status_code == 200:
                return response.json()["content"].strip()
            else:
                return f"Error: {response.text}"
        except Exception as e:
            return f"Exception in BitNet generation: {e}"

    def __del__(self):
        """Cleanup: Stop the server when the object is destroyed."""
        if self.server_process:
            print("🛑 Shutting down BitNet server...")
            if platform.system() == "Windows":
                self.server_process.terminate()
            else:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
