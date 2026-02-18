import subprocess
import os
import tempfile
import shutil
from ..base_module_adapter import BaseModuleAdapter

class WhisperAdapter(BaseModuleAdapter):
    def __init__(self):
        self.status = "Idle"
        self.root_dir = os.getcwd()
        self.whisper_cpp_path = os.path.join(self.root_dir, "whisper.cpp")
        
        # Search for binary (Prioritize C++ binaries)
        search_paths = [
            shutil.which("whisper-cli"),
            os.path.join(self.whisper_cpp_path, "build", "bin", "whisper-cli"),
            os.path.join(self.whisper_cpp_path, "build", "bin", "main"),
            shutil.which("whisper")
        ]
        self.cli_path = next((p for p in search_paths if p and os.path.exists(p) or (p and shutil.which(p))), "whisper-cli")
        
        # Search for default model
        default_model = "ggml-base.en.bin"
        self.model_path = os.path.join(self.root_dir, "whisper_models", default_model)
        if not os.path.exists(self.model_path):
            self.model_path = os.path.join(self.whisper_cpp_path, "models", default_model)

    def load(self, config):
        # Refresh binary path
        search_paths = [
            shutil.which("whisper-cli"),
            os.path.join(self.whisper_cpp_path, "build", "bin", "whisper-cli"),
            os.path.join(self.whisper_cpp_path, "build", "bin", "main"),
            shutil.which("whisper")
        ]
        self.cli_path = next((p for p in search_paths if p and os.path.exists(p) or (p and shutil.which(p))), "whisper-cli")

        model_name = config.get("model")
        if model_name:
            if not model_name.startswith("ggml-") and not model_name.endswith(".bin"):
                model_name = f"ggml-{model_name}.bin"
            elif not model_name.endswith(".bin"):
                model_name = f"{model_name}.bin"
            
            # Check multiple model locations
            found = False
            for folder in ["whisper_models", os.path.join("whisper.cpp", "models")]:
                check_path = os.path.join(self.root_dir, folder, model_name)
                if os.path.exists(check_path):
                    self.model_path = check_path
                    found = True
                    break
            
            if not found:
                self.status = f"Error: {model_name} not found"
                return False
        
        self.status = "Running"
        return True

    def unload(self):
        self.status = "Idle"

    def generate(self, wav_path, params):
        try:
            command = [
                self.cli_path,
                "-m", self.model_path,
                "-f", wav_path,
                "-t", str(params.get("threads", 4)),
                "-otxt",
                "-nt",
                "-np" # No prints (suppress progress)
            ]
            
            print(f"🎙️ Running Whisper transcription: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Whisper transcription failed (code {result.returncode}): {result.stderr}")
                return f"Error: {result.stderr}"

            txt_path = wav_path + ".txt"
            
            if os.path.exists(txt_path):
                with open(txt_path, "r") as tf:
                    text = tf.read().strip()
                os.remove(txt_path)
                return text
            
            return result.stdout.strip()
        except Exception as e:
            print(f"❌ Whisper adapter exception: {e}")
            return f"Error: {e}"

    def get_status(self):
        return {
            "status": self.status,
            "model": os.path.basename(self.model_path)
        }
