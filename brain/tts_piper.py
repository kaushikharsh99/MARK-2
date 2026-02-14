import subprocess
import os
import shlex

class PiperTTSController:
    def __init__(self, piper_exe=None, model_path=None):
        # Default paths relative to MARK-2 root
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if piper_exe:
            self.piper_exe = piper_exe
        else:
            # Look for piper binary in MARK-2/piper/piper
            self.piper_exe = os.path.join(self.root_dir, "piper", "piper")
            
        if model_path:
            self.model_path = model_path
        else:
            # Look for voice model in MARK-2/voices/
            self.model_path = os.path.join(self.root_dir, "voices", "en_US-ryan-high.onnx")

    def speak(self, text):
        if not text:
            return
        print(f"🗣️ Jarvis: {text}")
        
        # We need to make sure the environment has the necessary libraries for piper
        piper_dir = os.path.dirname(self.piper_exe)
        env = os.environ.copy()
        
        # Add piper dir to LD_LIBRARY_PATH for its shared objects
        if os.path.exists(piper_dir):
            if "LD_LIBRARY_PATH" in env:
                env["LD_LIBRARY_PATH"] = f"{piper_dir}:{env['LD_LIBRARY_PATH']}"
            else:
                env["LD_LIBRARY_PATH"] = piper_dir

        try:
            # 1. Start Piper process
            piper_cmd = [
                self.piper_exe,
                "--model", self.model_path,
                "--output_raw"
            ]
            
            # 2. Start aplay process
            aplay_cmd = [
                "aplay",
                "-r", "22050",
                "-f", "S16_LE",
                "-t", "raw",
                "-"
            ]

            # Chain them together
            p1 = subprocess.Popen(piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
            p2 = subprocess.Popen(aplay_cmd, stdin=p1.stdout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            p1.stdout.close()
            p1.communicate(input=text.encode('utf-8'))
            p2.wait()

        except Exception as e:
            print(f"Error in Piper TTS: {e}")
