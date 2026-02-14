#!/bin/bash

# J.A.R.V.I.S. MARK-2 - Ultra-Robust Automated Installation Script
# Optimized for CPU-only performance on Linux (Fedora/Ubuntu)

echo "🤖 Starting J.A.R.V.I.S. MARK-2 Setup..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. System Dependencies
echo "📦 Checking system dependencies..."
if [ -f /etc/fedora-release ]; then
    sudo dnf install -y git cmake gcc-c++ make portaudio-devel python3-devel alsa-utils wget tar clang
elif [ -f /etc/debian_version ]; then
    sudo apt update
    sudo apt install -y git build-essential cmake portaudio19-dev python3-all-dev alsa-utils wget tar clang
else
    echo "⚠️ Unknown OS. Please ensure you have git, cmake, build-essential, clang, and portaudio-dev installed."
fi

# 2. Python Environment
echo "🐍 Setting up Python environment..."
# Create venv in a stable location
VENV_DIR="$SCRIPT_DIR/BitNet/bitnet_env"
if [ ! -d "$VENV_DIR" ]; then
    mkdir -p "$SCRIPT_DIR/BitNet"
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# Ensure we use the venv's python/pip for everything
export PATH="$VENV_DIR/bin:$PATH"

echo "Creating .env file..."
echo "PICOVOICE_ACCESS_KEY=Qvv+c3PAMdarQCAWbWdMjMG25cpSWJKZco0FnbEnUCFlG06F9e8S/Q==" > .env

echo "pip: Installing core requirements..."
pip install --upgrade pip
pip install SpeechRecognition pvporcupine pvrecorder soundfile rapidfuzz python-dotenv requests psutil pyaudio numpy huggingface_hub

# 3. Whisper.cpp Setup
echo "🎙️ Setting up Whisper.cpp..."
if [ ! -d "whisper.cpp/.git" ]; then
    echo "Cloning Whisper.cpp..."
    rm -rf whisper.cpp
    git clone https://github.com/ggerganov/whisper.cpp.git
fi
cd whisper.cpp
cmake -B build
cmake --build build --config Release
echo "📥 Downloading Whisper base.en model..."
./models/download-ggml-model.sh base.en
cd "$SCRIPT_DIR"

# 4. BitNet Setup
echo "🧠 Setting up BitNet 1.58..."
if [ ! -f "BitNet/setup_env.py" ]; then
    echo "BitNet repo missing or incomplete. Cloning..."
    # Keep the venv!
    mv "$VENV_DIR" "$SCRIPT_DIR/bitnet_env_backup"
    rm -rf BitNet
    git clone --recursive https://github.com/microsoft/BitNet.git
    mv "$SCRIPT_DIR/bitnet_env_backup" "$VENV_DIR"
fi

cd BitNet
source bitnet_env/bin/activate
echo "pip: Installing BitNet specific requirements..."
pip install -r requirements.txt

echo "📥 Downloading BitNet 2B model..."
# Use python -m to ensure we use the correct one
python3 -m huggingface_hub.commands.hf_cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T

# Force BitNet to use the current python for its internal calls
export PYTHON_EXECUTABLE=$(which python3)
python3 setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s

# Manual build fallback if setup_env.py didn't create the server
if [ ! -f "build/bin/llama-server" ]; then
    echo "⚠️ setup_env.py didn't build the server. Attempting manual build..."
    cmake -B build
    cmake --build build --config Release -j$(nproc)
fi
cd "$SCRIPT_DIR"

# 5. Piper TTS & Voice Setup
echo "🗣️ Setting up Piper TTS..."
if [ ! -d "piper" ]; then
    echo "📥 Downloading Piper binary..."
    wget -q --show-progress https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
    tar -xzf piper_amd64.tar.gz
    rm piper_amd64.tar.gz
fi

mkdir -p voices
cd voices
if [ ! -f "en_US-ryan-high.onnx" ]; then
    echo "📥 Downloading Ryan-High voice model..."
    wget -q --show-progress -O en_US-ryan-high.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx
    wget -q --show-progress -O en_US-ryan-high.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx.json
fi
cd "$SCRIPT_DIR"

# 6. Final Steps
echo "✨ Setup Complete!"
echo "-------------------------------------------------------"
echo "To run J.A.R.V.I.S. MARK-2:"
echo "Run: ./BitNet/bitnet_env/bin/python main.py"
echo "-------------------------------------------------------"
