import subprocess
import os
import tempfile
import soundfile as sf
import numpy as np

class WhisperCPPController:
    def __init__(self, model_path=None, whisper_cpp_path=None, threads=4):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if whisper_cpp_path:
            self.whisper_cpp_path = whisper_cpp_path
        else:
            self.whisper_cpp_path = os.path.join(self.root_dir, "whisper.cpp")
            
        self.cli_path = os.path.join(self.whisper_cpp_path, "build", "bin", "whisper-cli")
        
        if model_path:
            self.model_path = model_path
        else:
            self.model_path = os.path.join(self.whisper_cpp_path, "models", "ggml-base.en.bin")
            
        self.threads = threads

    def transcribe_path(self, wav_path):
        """Transcribes a wav file at the given path."""
        try:
            command = [
                self.cli_path,
                "-m", self.model_path,
                "-f", wav_path,
                "-t", str(self.threads),
                "-otxt",
                "-nt" # no timestamps
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            txt_path = wav_path + ".txt"
            if os.path.exists(txt_path):
                with open(txt_path, "r") as tf:
                    text = tf.read().strip()
                os.remove(txt_path)
                return text
            return result.stdout.strip()
        except Exception as e:
            print(f"Error in transcribe_path: {e}")
            return None

    def transcribe(self, audio_data):
        """
        Transcribes audio data using whisper-cli.
        audio_data: speech_recognition.AudioData object
        """
        # Convert audio data to PCM 16kHz Mono (required by whisper.cpp)
        pcm = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16).astype(np.float32)
        pcm /= 32768.0

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, pcm, 16000)
            wav_path = f.name

        try:
            command = [
                self.cli_path,
                "-m", self.model_path,
                "-f", wav_path,
                "-t", str(self.threads),
                "-otxt",
                "-nt" # no timestamps
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # whisper-cli with -otxt creates a file with .txt extension
                txt_path = wav_path + ".txt"
                if os.path.exists(txt_path):
                    with open(txt_path, "r") as tf:
                        text = tf.read().strip()
                    os.remove(txt_path)
                    return text
                else:
                    # Fallback to stdout if file not found
                    return result.stdout.strip()
            else:
                print(f"Error in Whisper.cpp: {result.stderr}")
                return None
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)

# Example usage:
# controller = WhisperCPPController()
# text = controller.transcribe(audio_data)
