#!/bin/bash

# J.A.R.V.I.S. MARK-2 - Final Automated Installation Script
# Following Official Microsoft BitNet (bitnet.cpp) steps for Fedora.

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

# 2. Python Environment (Conda preferred, fallback to venv)
echo "🐍 Setting up Python environment..."
if command -v conda &> /dev/null; then
    echo "Conda found. Creating 'bitnet-cpp' environment..."
    conda create -n bitnet-cpp python=3.9 -y
    # We need to use the full path to the conda python for subsequent commands
    PYTHON_EXE=$(conda info --base)/envs/bitnet-cpp/bin/python
    PIP_EXE=$(conda info --base)/envs/bitnet-cpp/bin/pip
else
    echo "Conda not found. Falling back to local venv (BitNet/bitnet_env)..."
    VENV_DIR="$SCRIPT_DIR/BitNet/bitnet_env"
    mkdir -p "$SCRIPT_DIR/BitNet"
    python3 -m venv "$VENV_DIR"
    PYTHON_EXE="$VENV_DIR/bin/python3"
    PIP_EXE="$VENV_DIR/bin/pip"
fi

echo "Creating .env file..."
echo "PICOVOICE_ACCESS_KEY=Qvv+c3PAMdarQCAWbWdMjMG25cpSWJKZco0FnbEnUCFlG06F9e8S/Q==" > .env

# 3. Core Requirements
echo "pip: Installing core requirements..."
$PIP_EXE install --upgrade pip setuptools wheel
$PIP_EXE install SpeechRecognition pvporcupine pvrecorder soundfile rapidfuzz python-dotenv requests psutil pyaudio numpy huggingface_hub

# 4. Whisper.cpp Setup
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

# 5. BitNet Setup (Official Microsoft Steps)
echo "🧠 Setting up BitNet 1.58..."
if [ ! -d "BitNet/.git" ]; then
    rm -rf BitNet
    git clone --recursive https://github.com/microsoft/BitNet.git
fi

cd BitNet
echo "pip: Installing BitNet dependencies..."
# Relax version pinning for newer systems
sed -i 's/torch~=2.2.1/torch>=2.2.1/g' requirements.txt 2>/dev/null
sed -i 's/numpy~=1.26.4/numpy>=1.26.4/g' requirements.txt 2>/dev/null
$PIP_EXE install -r requirements.txt
$PIP_EXE install ./3rdparty/llama.cpp/gguf-py

echo "📥 Downloading BitNet 2B model..."
$PYTHON_EXE -m huggingface_hub.commands.hf_cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T

echo "🛠️ Running Codegen & Build..."
# We MUST run setup_env.py to generate the bitnet-lut-kernels.h file
# but we force it to use our specific python executable
export PYTHON_EXECUTABLE=$PYTHON_EXE
$PYTHON_EXE setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s

# If the setup script didn't build the server (sometimes it only builds llama-cli), we force it
if [ ! -f "build/bin/llama-server" ]; then
    echo "⚠️ llama-server missing. Forcing manual build..."
    cmake -B build -DGGML_BITNET=ON -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
    cmake --build build --config Release -j$(nproc)
fi
cd "$SCRIPT_DIR"

# 6. Piper TTS Setup
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

echo "✨ Setup Complete!"
echo "-------------------------------------------------------"
echo "To run J.A.R.V.I.S. MARK-2:"
if command -v conda &> /dev/null; then
    echo "1. conda activate bitnet-cpp"
    echo "2. python main.py"
else
    echo "Run: ./BitNet/bitnet_env/bin/python main.py"
fi
echo "-------------------------------------------------------"
