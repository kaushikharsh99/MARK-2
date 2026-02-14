import os
from dotenv import load_dotenv
import pvporcupine
from pvrecorder import PvRecorder
import subprocess

# LOAD ENV VARIABLES
load_dotenv()

ACCESS_KEY = "Qvv+c3PAMdarQCAWbWdMjMG25cpSWJKZco0FnbEnUCFlG06F9e8S/Q=="

# In MARK-2 root
KEYWORD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Jarvis_en_linux_v4_0_0.ppn")

def init_wake_word_engine():
    """Initializes and returns the Porcupine wake word engine."""
    if not ACCESS_KEY:
        print("⚠️ PICOVOICE_ACCESS_KEY not found in environment. Wake word disabled.")
        return None
    
    try:
        return pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[KEYWORD_PATH]
        )
    except Exception as e:
        print(f"❌ Wake word engine init failed: {e}")
        return None

def wait_for_wake_word(porcupine_instance):
    """
    Waits for the wake word.
    """
    if porcupine_instance is None:
        return True # Fallback to always active if no engine

    recorder = PvRecorder(
        device_index=-1,
        frame_length=porcupine_instance.frame_length
    )
    recorder.start()

    print("🟢 Listening for 'Jarvis'...")

    try:
        while True:
            pcm = recorder.read()
            if porcupine_instance.process(pcm) >= 0:
                print("🟢 Wake word detected")
                return True
    finally:
        recorder.stop()
        recorder.delete()
