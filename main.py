import os
import time
import re
import gc
import speech_recognition as sr
import numpy as np

from wake import wait_for_wake_word, init_wake_word_engine
from brain.bitnet_controller import BitNetController
from brain.stt_whisper import WhisperCPPController
from brain.tts_piper import PiperTTSController

# ---------------- CONFIG ----------------

SAMPLE_RATE = 16000

# Conversational Persona Prompt
AGENT_SYSTEM_PROMPT = """You are Jarvis, a professional AI with a legendary sense of humor. 
Respond in a SINGLE, snappy, and genuinely funny sentence. 
Be helpful, but prioritize being entertaining and witty. Don't be afraid to be a bit sarcastic."""

# ---------------- UTILS ----------------

def clean_llm_output(text):
    """
    Cleans up the raw output from BitNet.
    """
    clean = re.sub(r'(User:|Jarvis:|Assistant:)', '', text, flags=re.IGNORECASE).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    return sentences[0] if sentences else clean

# ---------------- MAIN LOOP ----------------

def main():
    print("🧠 Initializing Jarvis MARK-2 (Talkative Mode Only)...")

    # Load core controllers
    llm = BitNetController() 
    stt = WhisperCPPController()
    tts = PiperTTSController()
    wake_engine = init_wake_word_engine()

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    print("✅ Jarvis is online. No tools, no RAG, just conversation.")

    try:
        while True:
            if wake_engine:
                wait_for_wake_word(wake_engine)
            
            tts.speak("Yes, sir?")
            
            with sr.Microphone(sample_rate=SAMPLE_RATE) as source:
                try:
                    print("🎙️ Listening...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    print("📝 Transcribing...")
                    text = stt.transcribe(audio)

                    if not text or len(text) < 2:
                        continue

                    print(f"👤 You: {text}")
                    
                    # Generate Response
                    prompt = f"{AGENT_SYSTEM_PROMPT}\nUser: {text}\nJarvis:"
                    print("🧠 Thinking...")
                    response = llm.generate(prompt, n_predict=64, temp=0.7)
                    
                    final_speech = clean_llm_output(response)
                    
                    if final_speech:
                        tts.speak(final_speech)
                    else:
                        tts.speak("I'm here, sir.")

                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Error: {e}")

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if wake_engine: wake_engine.delete()
        gc.collect()

if __name__ == "__main__":
    main()
