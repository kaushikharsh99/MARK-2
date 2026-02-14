# J.A.R.V.I.S. (MARK-2)

**Just A Rather Very Intelligent System - CPU Optimized Edition**

MARK-2 is the next evolution of J.A.R.V.I.S., rebuilt from the ground up for extreme performance on standard CPUs. By leveraging **BitNet 1.58** and **Whisper.cpp**, MARK-2 provides a snappy, conversational experience without the need for high-end GPUs.

## 🚀 What's New in MARK-2

*   **BitNet 1.58 LLM:** Uses the state-of-the-art 1-bit LLM (BitNet b1.58 2B) for rapid local inference.
*   **Persistent LLM Server:** The model stays loaded in RAM for near-instant response times.
*   **Whisper.cpp STT:** Ultra-fast C++ implementation of OpenAI's Whisper for local speech-to-text.
*   **High-Quality TTS:** Upgraded to **Ryan-High** Piper voice for a clearer, more natural-sounding butler.
*   **Lean Architecture:** Stripped of heavy dependencies to focus on a fast, humorous conversational experience.
*   **Persona Engine:** Optimized for witty, professional, and snarky one-liner responses.

## 🛠️ Architecture

*   **STT:** Whisper.cpp (base.en)
*   **Brain:** BitNet b1.58 2B (Persistent llama-server)
*   **TTS:** Piper (Ryan-High voice)
*   **KWS:** Picovoice Porcupine ("Jarvis" wake word)

## 📦 Prerequisites

1.  **Linux Environment** (Fedora/Ubuntu recommended)
2.  **Picovoice Access Key:** Get a free key from the [Picovoice Console](https://console.picovoice.ai/).
3.  **Built Binaries:**
    *   `whisper-cli` (built in `whisper.cpp/build/bin/`)
    *   `llama-server` (built in `BitNet/build/bin/`)

## 🚀 Installation & Setup

1.  **Clone & Environment:**
    ```bash
    cd MARK-2
    # Ensure you have the BitNet environment set up
    source BitNet/bitnet_env/bin/activate
    pip install -r requirements.txt
    ```

2.  **Environment Variables:**
    Create a `.env` file in the `MARK-2` directory:
    ```env
    PICOVOICE_ACCESS_KEY=your_key_here
    ```

3.  **Model Placement:**
    *   BitNet: `BitNet/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf`
    *   Whisper: `whisper.cpp/models/ggml-base.en.bin`
    *   Voice: `voices/en_US-ryan-high.onnx`

## 🖥️ Usage

Run the main script using the provided environment:

```bash
./BitNet/bitnet_env/bin/python main.py
```

*   **Wake Word:** Say "Jarvis" to trigger the listener.
*   **Conversation:** Speak naturally; Jarvis will respond with snappy, humorous one-liners.

## 📜 Project Goals

MARK-2 focuses on the core conversational loop, providing a fast and reliable base for a local AI butler that feels alive and responsive on standard hardware.
