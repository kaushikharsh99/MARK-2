#!/bin/bash

set -e

echo "🤖 Starting J.A.R.V.I.S. MARK-2 Setup..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ==============================
# 1️⃣ System Dependencies (Fedora)
# ==============================

echo "📦 Installing system dependencies..."

sudo dnf install -y git cmake gcc gcc-c++ make python3 \
    portaudio-devel alsa-utils wget tar clang libgomp

# ==============================
# 2️⃣ Create Conda Environment
# ==============================

echo "🐍 Setting up Conda environment..."

conda remove -n bitnet-cpp --all -y 2>/dev/null || true
conda create -n bitnet-cpp python=3.9 -y

eval "$(conda shell.bash hook)"
conda activate bitnet-cpp

pip install --upgrade pip
pip install huggingface_hub numpy


# ==============================
# 4️⃣ Install Whisper.cpp
# ==============================

echo "🎙️ Installing Whisper.cpp..."

rm -rf whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j$(nproc)

./models/download-ggml-model.sh base.en

cd "$SCRIPT_DIR"

# ==============================
# 5️⃣ Install Piper
# ==============================

echo "🗣️ Installing Piper..."

rm -rf piper
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz
rm piper_amd64.tar.gz

mkdir -p voices
cd voices

wget -O en_US-ryan-high.onnx \
    https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx

wget -O en_US-ryan-high.onnx.json \
    https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx.json

cd "$SCRIPT_DIR"

# ==============================
# Done
# ==============================

echo ""
echo "✨ Setup Complete!"
echo "-------------------------------------------------------"
echo "Activate environment:"
echo "conda activate bitnet-cpp"
echo ""
echo "Whisper installed at: whisper.cpp"
echo "Piper installed at: piper/"
echo ""
echo "BitNet must be installed manually (see instructions above)."
echo "-------------------------------------------------------"
# ==============================
# 3️⃣ BitNet (Manual Install Only)
# ==============================

echo "⚠️ BitNet installation is now manual."
echo ""
echo "To install BitNet manually:"
echo "-------------------------------------------------------"
echo "git clone --recursive https://github.com/microsoft/BitNet.git"
echo "cd BitNet"
echo "pip install -r requirements.txt"
echo ""
echo "# Download model"
echo "mkdir -p models/BitNet-b1.58-2B-4T"
echo "huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T"
echo ""
echo "# Build"
echo "mkdir build && cd build"
echo "cmake .."
echo "make -j\$(nproc)"
echo "-------------------------------------------------------"
echo ""
