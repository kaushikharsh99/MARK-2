#!/bin/bash

# J.A.R.V.I.S. MARK-2 - Automated Installation Script
# Optimized for CPU-only performance on Linux (Fedora/Ubuntu)

echo "🤖 Starting J.A.R.V.I.S. MARK-2 Setup..."

# 1. System Dependencies
echo "📦 Checking system dependencies..."
if [ -f /etc/fedora-release ]; then
    sudo dnf install -y git cmake gcc-c++ make portaudio-devel python3-devel alsa-utils
elif [ -f /etc/debian_version ]; then
    sudo apt update
    sudo apt install -y git build-essential cmake portaudio19-dev python3-all-dev alsa-utils
else
    echo "⚠️ Unknown OS. Please ensure you have git, cmake, build-essential, and portaudio-dev installed."
fi

# 2. Python Environment
echo "🐍 Setting up Python environment..."
python3 -m venv BitNet/bitnet_env
source BitNet/bitnet_env/bin/activate

echo "Creating .env file..."
echo "PICOVOICE_ACCESS_KEY=Qvv+c3PAMdarQCAWbWdMjMG25cpSWJKZco0FnbEnUCFlG06F9e8S/Q==" > .env

echo "pip: Installing core requirements..."
pip install --upgrade pip
pip install SpeechRecognition pvporcupine pvrecorder soundfile rapidfuzz python-dotenv requests psutil pyaudio numpy

# 3. Whisper.cpp Setup
echo "🎙️ Setting up Whisper.cpp..."
if [ ! -d "whisper.cpp" ]; then
    git clone https://github.com/ggerganov/whisper.cpp.git
fi
cd whisper.cpp
cmake -B build
cmake --build build --config Release
echo "📥 Downloading Whisper base.en model..."
./models/download-ggml-model.sh base.en
cd ..

# 4. BitNet Setup
echo "🧠 Setting up BitNet 1.58..."
if [ ! -d "BitNet" ]; then
    git clone --recursive https://github.com/microsoft/BitNet.git
fi
cd BitNet
# Use the same environment
pip install -r requirements.txt
echo "📥 Downloading BitNet 2B model..."
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s
cd ..

# 5. Piper Voice Model
echo "🗣️ Setting up Piper Voice..."
mkdir -p voices
cd voices
if [ ! -f "en_US-ryan-high.onnx" ]; then
    echo "📥 Downloading Ryan-High voice model..."
    wget -O en_US-ryan-high.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx
    wget -O en_US-ryan-high.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx.json
fi
cd ..

# 6. Final Steps
echo "✨ Setup Complete!"
echo "-------------------------------------------------------"
echo "To run J.A.R.V.I.S. MARK-2:"
echo "Run: ./BitNet/bitnet_env/bin/python main.py"
echo "-------------------------------------------------------"
