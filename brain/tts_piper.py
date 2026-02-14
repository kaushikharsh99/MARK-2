import subprocess
import os
import shlex

class PiperTTSController:
    def __init__(self, piper_exe=None, model_path=None):
        # Default paths relative to project root
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        if piper_exe:
            self.piper_exe = piper_exe
        else:
            self.piper_exe = os.path.join(self.project_root, "MARK-1", "piper_bin", "piper", "piper")
            
        if model_path:
            self.model_path = model_path
        else:
            self.model_path = os.path.join(self.project_root, "MARK-2", "voices", "en_US-ryan-high.onnx")

    def speak(self, text):
        if not text:
            return
        print(f"🗣️ Jarvis: {text}")
        
        # We need to make sure the environment has the necessary libraries for piper
        piper_dir = os.path.dirname(self.piper_exe)
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = piper_dir + (f":{env['LD_LIBRARY_PATH']}" if "LD_LIBRARY_PATH" in env else "")

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

            # Chain them together without using shell=True for the text input
            p1 = subprocess.Popen(piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
            p2 = subprocess.Popen(aplay_cmd, stdin=p1.stdout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Close p1 stdout so it can receive SIGPIPE
            p1.stdout.close()
            
            # Send the text to Piper's stdin
            p1.communicate(input=text.encode('utf-8'))
            
            # Wait for audio to finish
            p2.wait()

        except Exception as e:
            print(f"Error in Piper TTS: {e}")

# Example usage:
# tts = PiperTTSController()
# tts.speak("Hello boss")
