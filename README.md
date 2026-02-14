# J.A.R.V.I.S. (MARK-2)

**Just A Rather Very Intelligent System - CPU Optimized Edition**

MARK-2 is a high-performance, voice-activated AI assistant rebuilt for local execution on standard CPUs. It leverages **BitNet 1.58** for rapid reasoning and **Whisper.cpp** for low-latency transcription.

## 🚀 Key Features
*   **BitNet 1.58 (2B):** Cutting-edge 1-bit LLM for near-instant local processing on CPU.
*   **Whisper.cpp:** High-speed, C++ optimized local Speech-to-Text.
*   **Piper TTS:** Clear and natural voice output using the **Ryan-High** model.
*   **Persona Engine:** Optimized for witty, professional, and snarky one-liner responses.

## 🛠️ Proper Manual Installation

Follow these steps to build the system properly on Fedora:

### 1. Install System Dependencies
```bash
sudo dnf install -y git cmake gcc gcc-c++ make python3 portaudio-devel alsa-utils wget tar clang libgomp
```

### 2. Setup Conda Environment
If you don't have Conda, the `installation_script.sh` can install it for you, or you can install Miniconda manually.
```bash
conda create -n bitnet-cpp python=3.9 -y
conda activate bitnet-cpp
```

### 3. Clone Properly (Recursive)
```bash
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet
git submodule update --init --recursive
```

### 4. Install Requirements
```bash
pip install -r requirements.txt
pip install ../ # installs jarvis core deps
```

### 5. Build Correctly
```bash
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
```

## 📦 Automated Installation (Recommended)

Alternatively, run the automated script which performs all the "Proper" steps above, including Python 3.14 compatibility fixes:

```bash
chmod +x installation_script.sh
./installation_script.sh
```

## 🖥️ Usage

```bash
conda activate bitnet-cpp
python main.py
```

*   **To Wake Up:** Say **"Jarvis"**.
*   **To Interact:** Speak naturally. Jarvis is optimized for one-liner responses.
