# J.A.R.V.I.S. (MARK-2)

**Just A Rather Very Intelligent System - CPU Optimized Edition**

MARK-2 is a high-performance, voice-activated AI assistant rebuilt for local execution on standard CPUs. It leverages **BitNet 1.58** for rapid reasoning and **Whisper.cpp** for low-latency transcription.

## 🚀 Key Features
*   **BitNet 1.58 (2B):** Cutting-edge 1-bit LLM for near-instant local processing on CPU.
*   **Whisper.cpp:** High-speed, C++ optimized local Speech-to-Text.
*   **Piper TTS:** Clear and natural voice output using the **Ryan-High** model.
*   **Persistent Memory:** Model stays loaded in RAM for a fluid, conversational experience.
*   **Humorous Persona:** Pre-configured with a snappy, witty, and slightly sarcastic butler personality.

## 🛠️ Requirements
*   **OS:** Linux (Fedora, Ubuntu, or Debian recommended).
*   **Hardware:** 8GB+ RAM recommended (CPU-only).
*   **Dependencies:** The installation script will automatically check for and install `cmake`, `clang`, `git`, and `portaudio`.

## 📦 Installation (Recommended)

The easiest way to set up J.A.R.V.I.S. is using the provided automated script. This will clone dependencies, compile the C++ binaries, set up the Python environment, and download all necessary models.

1.  **Clone this repository:**
    ```bash
    git clone https://github.com/kaushikharsh99/MARK-2.git
    cd MARK-2
    ```

2.  **Run the installation script:**
    ```bash
    chmod +x installation_script.sh
    ./installation_script.sh
    ```

## 🖥️ Usage

Once the setup is complete, you can start J.A.R.V.I.S. with a single command:

```bash
./BitNet/bitnet_env/bin/python main.py
```

*   **To Wake Up:** Say **"Jarvis"**.
*   **To Interact:** Speak naturally. Jarvis is optimized for one-liner responses and will respond with his signature wit.

## 📜 Technical Stack
*   **Brain:** BitNet b1.58 2B (via llama-server)
*   **STT:** Whisper.cpp (base.en)
*   **TTS:** Piper (Ryan-High)
*   **KWS:** Picovoice Porcupine
