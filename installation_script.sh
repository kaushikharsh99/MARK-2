#!/bin/bash

# J.A.R.V.I.S. MARK-2 - Final Ultra-Robust Installation Script
# This script bypasses broken upstream setup scripts and builds BitNet manually.

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
VENV_DIR="$SCRIPT_DIR/BitNet/bitnet_env"
mkdir -p "$SCRIPT_DIR/BitNet"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

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
cmake --build build --config Release -j$(nproc)
echo "📥 Downloading Whisper base.en model..."
./models/download-ggml-model.sh base.en
cd "$SCRIPT_DIR"

# 4. BitNet Setup (Manual Build)
echo "🧠 Setting up BitNet 1.58..."
if [ ! -d "BitNet/.git" ]; then
    echo "Cloning BitNet..."
    rm -rf BitNet
    git clone --recursive https://github.com/microsoft/BitNet.git
fi

# Move venv back in if we just recloned
if [ ! -d "BitNet/bitnet_env" ]; then
    mkdir -p BitNet
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

cd BitNet
echo "pip: Installing BitNet dependencies..."
pip install -r requirements.txt
pip install ./3rdparty/llama.cpp/gguf-py

echo "📥 Downloading BitNet 2B model..."
python3 -m huggingface_hub.commands.hf_cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T

echo "🛠️ Compiling BitNet manually (Bypassing broken setup_env.py)..."
cmake -B build -DGGML_BITNET=ON
cmake --build build --config Release -j$(nproc)

# Verify build
if [ ! -f "build/bin/llama-server" ]; then
    echo "❌ Manual build failed. Please check the logs above."
    exit 1
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
