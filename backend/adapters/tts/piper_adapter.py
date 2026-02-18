import subprocess
import os
import shutil
import json
import wave
from ..base_module_adapter import BaseModuleAdapter

class PiperAdapter(BaseModuleAdapter):
    def __init__(self):
        self.status = "Idle"
        self.root_dir = os.getcwd()
        # Binary location confirmed by user
        self.piper_exe = os.path.join(self.root_dir, "piper", "piper")
        
        # Verify if local binary is valid
        if not os.path.exists(self.piper_exe):
            # Fallback search
            sys_piper = shutil.which("piper")
            if sys_piper:
                self.piper_exe = sys_piper

        # Default model path in the new structure
        self.model_path = os.path.join(self.root_dir, "piper", "voices", "en_US-ryan-high.onnx")

    def load(self, config):
        if not os.path.exists(self.piper_exe):
            self.status = "Error: piper binary not found"
            return False
            
        model_name = config.get("model")
        if model_name:
            if not model_name.endswith(".onnx"):
                model_name += ".onnx"
            
            # Check the new voices directory
            check_path = os.path.join(self.root_dir, "piper", "voices", model_name)
            if os.path.exists(check_path):
                self.model_path = check_path
            else:
                # Fallback to old voices folder or piper root
                fallback_paths = [
                    os.path.join(self.root_dir, "voices", model_name),
                    os.path.join(self.root_dir, "piper", model_name)
                ]
                found = False
                for p in fallback_paths:
                    if os.path.exists(p):
                        self.model_path = p
                        found = True
                        break
                
                if not found:
                    self.status = f"Error: {model_name} not found"
                    return False
                
        self.status = "Running"
        return True

    def generate(self, text, params):
        output_wav = params.get("output_path")
        if not output_wav: return None

        # Environment handling
        piper_dir = os.path.dirname(self.piper_exe)
        env = os.environ.copy()
        if os.path.exists(piper_dir):
            if "LD_LIBRARY_PATH" in env:
                env["LD_LIBRARY_PATH"] = f"{piper_dir}:{env['LD_LIBRARY_PATH']}"
            else:
                env["LD_LIBRARY_PATH"] = piper_dir

        # Get sample rate from config json
        sample_rate = 22050
        config_path = self.model_path + ".json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                    sample_rate = cfg.get("audio", {}).get("sample_rate", 22050)
            except: pass

        try:
            print(f"🔊 Piper: {self.model_path} ({sample_rate}Hz)")
            
            piper_cmd = [
                self.piper_exe,
                "--model", self.model_path,
                "--output_raw"
            ]
            
            p1 = subprocess.Popen(
                piper_cmd, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                env=env
            )
            
            pcm_data, stderr_data = p1.communicate(input=text.encode('utf-8'))
            
            if p1.returncode != 0:
                print(f"❌ Piper process failed: {stderr_data.decode()}")
                return None

            # Local playback
            try:
                aplay_cmd = ["aplay", "-r", str(sample_rate), "-f", "S16_LE", "-t", "raw", "-"]
                aplay_proc = subprocess.Popen(aplay_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                aplay_proc.communicate(input=pcm_data)
            except: pass

            # Save to WAV for UI
            with wave.open(output_wav, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_data)
                
            return output_wav
        except Exception as e:
            print(f"❌ TTS Exception: {e}")
            return None

    def unload(self):
        self.status = "Idle"

    def get_status(self):
        return {
            "status": self.status,
            "model": os.path.basename(self.model_path)
        }
