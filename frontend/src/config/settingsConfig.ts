export const settingsConfig: Record<string, { title: string; fields: Array<{ label: string; type: "text" | "select" | "slider" | "toggle"; description?: string; options?: string[]; min?: number; max?: number; step?: number; defaultValue?: string | number | boolean; advanced?: boolean }> }> = {
  llm: {
    title: "LLM Settings",
    fields: [
      { 
        label: "Model Provider", 
        type: "select", 
        description: "Select the backend provider for the language model.", 
        options: ["BitNet", "Llama.cpp", "Ollama", "vLLM"], 
        defaultValue: "BitNet" 
      },
      { label: "Model", type: "select", description: "Select the language model to use for responses.", options: ["BitNet 2B"], defaultValue: "BitNet 2B" },
      { label: "Temperature", type: "slider", description: "Controls randomness. Lower values are more deterministic.", min: 0, max: 2, step: 0.1, defaultValue: 0.7 },
      { label: "Max Tokens", type: "slider", description: "Maximum number of tokens in the response.", min: 256, max: 4096, step: 256, defaultValue: 2048 },
      { label: "Context Window", type: "slider", description: "Number of tokens the model can consider.", min: 512, max: 32768, step: 512, defaultValue: 2048, advanced: true },
      { label: "CPU Threads", type: "slider", description: "Number of CPU threads to use for inference.", min: 1, max: 64, step: 1, defaultValue: 4, advanced: true },
      { label: "GPU Layers", type: "slider", description: "Number of layers to offload to GPU (0 for CPU only).", min: 0, max: 128, step: 1, defaultValue: 0, advanced: true },
      { label: "System Prompt", type: "text", description: "Instructions that define the assistant's behavior.", defaultValue: "You are JARVIS, a helpful AI assistant." },
      { label: "Top P", type: "slider", description: "Nucleus sampling threshold.", min: 0, max: 1, step: 0.05, defaultValue: 1, advanced: true },
      { label: "Frequency Penalty", type: "slider", description: "Reduces repetition of token sequences.", min: 0, max: 2, step: 0.1, defaultValue: 0, advanced: true },
      { label: "Stream Responses", type: "toggle", description: "Display responses as they are generated.", defaultValue: true, advanced: true },
    ],
  },
  asr: {
    title: "ASR Settings",
    fields: [
      { 
        label: "ASR Provider", 
        type: "select", 
        description: "Select the backend provider for speech recognition.", 
        options: ["Whisper.cpp", "Faster-Whisper", "Vosk"], 
        defaultValue: "Whisper.cpp" 
      },
      { label: "Model", type: "select", description: "Select the ASR model to use.", options: ["tiny", "base", "small"], defaultValue: "base" },
      { label: "Language", type: "select", description: "Language for speech recognition.", options: ["Auto", "English", "Spanish", "French", "German"], defaultValue: "Auto" },
      { label: "Enabled", type: "toggle", description: "Enable automatic speech recognition.", defaultValue: true },
      { label: "Silence Detection", type: "toggle", description: "Automatically detect end of speech.", defaultValue: true, advanced: true },
      { label: "Noise Suppression", type: "toggle", description: "Filter background noise.", defaultValue: false, advanced: true },
    ],
  },
  tts: {
    title: "TTS Settings",
    fields: [
      { 
        label: "TTS Provider", 
        type: "select", 
        description: "Select the backend provider for speech output.", 
        options: ["Piper (Local)", "Coqui TTS", "XTTS"], 
        defaultValue: "Piper (Local)" 
      },
      { label: "Model", type: "select", description: "Select the voice model to use.", options: ["en_US-ryan-high"], defaultValue: "en_US-ryan-high" },
      { label: "Speed", type: "slider", description: "Speech rate multiplier.", min: 0.5, max: 2, step: 0.1, defaultValue: 1 },
      { label: "Enabled", type: "toggle", description: "Enable text-to-speech output.", defaultValue: true },
      { label: "Auto-play Responses", type: "toggle", description: "Automatically speak AI responses.", defaultValue: false, advanced: true },
    ],
  },
  rag: {
    title: "RAG Settings",
    fields: [
      { label: "Vector Store", type: "select", description: "Backend for vector storage.", options: ["ChromaDB", "FAISS"], defaultValue: "ChromaDB" },
      { label: "Embedding Model", type: "select", description: "Model for generating embeddings.", options: ["all-MiniLM-L6-v2", "bge-small-en-v1.5"], defaultValue: "all-MiniLM-L6-v2" },
      { label: "Enabled", type: "toggle", description: "Enable retrieval-augmented generation.", defaultValue: false },
      { label: "Chunk Size", type: "slider", description: "Size of text chunks for indexing.", min: 128, max: 2048, step: 128, defaultValue: 512, advanced: true },
      { label: "Top K Results", type: "slider", description: "Number of relevant chunks to retrieve.", min: 1, max: 20, step: 1, defaultValue: 5, advanced: true },
    ],
  },
  tools: {
    title: "Tools",
    fields: [
      { label: "Web Search", type: "toggle", description: "Allow searching the web for information.", defaultValue: true },
      { label: "Code Interpreter", type: "toggle", description: "Execute code in a sandboxed environment.", defaultValue: false },
      { label: "File Upload", type: "toggle", description: "Allow file uploads for analysis.", defaultValue: true },
      { label: "Image Generation", type: "toggle", description: "Generate images from text descriptions.", defaultValue: false },
      { label: "API Calling", type: "toggle", description: "Enable external API integrations.", defaultValue: false, advanced: true },
    ],
  },
};
