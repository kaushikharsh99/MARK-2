#!/bin/bash

# J.A.R.V.I.S. MARK-2 - Ultimate "Zero-to-Hero" Installation Script
# This script installs Miniconda (if missing), sets up the environment, and builds everything.

echo "🤖 Starting J.A.R.V.I.S. MARK-2 Setup..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. System Dependencies
echo "📦 Checking system dependencies..."
if [ -f /etc/fedora-release ]; then
    sudo dnf install -y git cmake gcc gcc-c++ make python3 portaudio-devel alsa-utils wget tar clang libgomp
elif [ -f /etc/debian_version ]; then
    sudo apt update
    sudo apt install -y git build-essential cmake portaudio19-dev python3-all-dev alsa-utils wget tar clang libgomp1
fi

# 2. Install Miniconda if missing
if ! command -v conda &> /dev/null; then
    echo "🔍 Conda not found. Installing Miniconda..."
    wget -q --show-progress https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p $HOME/miniconda3
    rm miniconda.sh
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda init bash
else
    echo "✅ Conda already installed."
    source "$(conda info --base)/etc/profile.d/conda.sh"
fi

# 3. Create & Setup Conda Env
echo "🐍 Setting up 'bitnet-cpp' Conda environment..."
if conda env list | grep -q "bitnet-cpp"; then
    echo "Environment exists. Updating..."
else
    conda create -n bitnet-cpp python=3.9 -y
fi

# Set binary paths for the environment
PYTHON_EXE="$(conda info --base)/envs/bitnet-cpp/bin/python"
PIP_EXE="$(conda info --base)/envs/bitnet-cpp/bin/pip"

# 4. Install all Python dependencies
echo "pip: Installing all requirements into Conda environment..."
$PIP_EXE install --upgrade pip setuptools wheel
$PIP_EXE install SpeechRecognition pvporcupine pvrecorder soundfile rapidfuzz python-dotenv requests psutil pyaudio numpy huggingface_hub

# 5. Whisper.cpp Setup
echo "🎙️ Setting up Whisper.cpp..."
if [ ! -d "whisper.cpp/.git" ]; then
    rm -rf whisper.cpp
    git clone https://github.com/ggerganov/whisper.cpp.git
fi
cd whisper.cpp
cmake -B build
cmake --build build --config Release -j$(nproc)
echo "📥 Downloading Whisper base.en model..."
./models/download-ggml-model.sh base.en
cd "$SCRIPT_DIR"

# 6. BitNet Setup (Official Microsoft Steps)
echo "🧠 Setting up BitNet 1.58..."
if [ ! -d "BitNet/.git" ]; then
    rm -rf BitNet
    git clone --recursive https://github.com/microsoft/BitNet.git
fi

cd BitNet
echo "pip: Installing BitNet specific dependencies..."
# Relax version pinning for newer systems
sed -i 's/torch~=2.2.1/torch>=2.2.1/g' requirements.txt 2>/dev/null
sed -i 's/numpy~=1.26.4/numpy>=1.26.4/g' requirements.txt 2>/dev/null
$PIP_EXE install -r requirements.txt
$PIP_EXE install ./3rdparty/llama.cpp/gguf-py

echo "📥 Downloading BitNet 2B model..."
$PYTHON_EXE -m huggingface_hub.commands.hf_cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T

echo "🛠️ Running Codegen & Build..."
export PYTHON_EXECUTABLE=$PYTHON_EXE
$PYTHON_EXE setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s

# Fallback build if setup_env.py didn't create server
if [ ! -f "build/bin/llama-server" ]; then
    echo "⚠️ llama-server missing. Forcing manual build..."
    cmake -B build -DGGML_BITNET=ON -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
    cmake --build build --config Release -j$(nproc)
fi
cd "$SCRIPT_DIR"

# 7. Piper TTS Setup
echo "🗣️ Setting up Piper TTS..."
if [ ! -d "piper" ]; then
    wget -q --show-progress https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
    tar -xzf piper_amd64.tar.gz
    rm piper_amd64.tar.gz
fi

mkdir -p voices
cd voices
if [ ! -f "en_US-ryan-high.onnx" ]; then
    wget -q --show-progress -O en_US-ryan-high.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx
    wget -q --show-progress -O en_US-ryan-high.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx.json
fi
cd "$SCRIPT_DIR"

# 8. Final configuration
echo "Creating .env file..."
echo "PICOVOICE_ACCESS_KEY=Qvv+c3PAMdarQCAWbWdMjMG25cpSWJKZco0FnbEnUCFlG06F9e8S/Q==" > .env

echo "✨ Setup Complete!"
echo "-------------------------------------------------------"
echo "To run J.A.R.V.I.S. MARK-2:"
echo "1. conda activate bitnet-cpp"
echo "2. python main.py"
echo "-------------------------------------------------------"
