# J.A.R.V.I.S. (MARK-2)

**Just A Rather Very Intelligent System - CPU Optimized Edition**

MARK-2 is a high-performance, voice-activated AI assistant rebuilt for local execution on standard CPUs. It leverages **BitNet 1.58** for rapid reasoning and **Whisper.cpp** for low-latency transcription.

## 🚀 Key Features
*   **BitNet 1.58 (2B):** Cutting-edge 1-bit LLM for near-instant local processing on CPU.
*   **Whisper.cpp:** High-speed, C++ optimized local Speech-to-Text.
*   **Piper TTS:** Clear and natural voice output using the **Ryan-High** model.
*   **Persona Engine:** Optimized for witty, professional, and snarky one-liner responses.

## 🛠️ Installation

The setup is divided into two parts: an automated script for core dependencies and a manual build for the BitNet inference engine.

### 1. Automated Setup (Core Dependencies)
The provided script handles system packages, STT/TTS engines, and Python environments.

```bash
chmod +x installation_script.sh
./installation_script.sh
```

### 2. Manual BitNet Setup (Critical)
You must manually clone and compile Microsoft's **BitNet** repository inside the `MARK-2` project folder.

1.  **Clone the Repository:**
    Navigate to your `MARK-2` directory and clone the official repo:
    ```bash
    git clone --recursive https://github.com/microsoft/BitNet
    cd BitNet
    ```

2.  **Install Requirements:**
    ```bash
    conda activate bitnet-cpp
    pip install -r requirements.txt
    ```

3.  **Build the Engine:**
    ```bash
    mkdir build
    cd build
    cmake -DCMAKE_BUILD_TYPE=Release ..
    make -j$(nproc)
    ```

**Note:** Ensure the resulting `BitNet` folder is located directly inside the `MARK-2` directory for the controller to function correctly.

## 🖥️ Usage

```bash
conda activate bitnet-cpp
python main.py
```

*   **To Wake Up:** Say **"Jarvis"**.
*   **To Interact:** Speak naturally. Jarvis is optimized for one-liner responses.
