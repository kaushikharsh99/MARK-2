import { useState, useRef, useEffect, useCallback } from "react";
import {
  Send,
  Menu,
  ArrowDown,
  Copy,
  Check,
  RefreshCw,
  Trash2,
  Square,
  Download,
  Clock,
  Hash,
  Mic,
  MicOff,
  Paperclip,
  Image as ImageIcon,
  FileText,
  X
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Message, AppSettings, AppStatus } from "@/types";
import { toast } from "sonner";
import axios from "axios";

interface ChatAreaProps {
  messages: Message[];
  onSendMessage: (content: string, speakResponse?: boolean) => void;
  onToggleSidebar: () => void;
  onDeleteMessage: (id: string) => void;
  onRegenerateMessage: (id: string) => void;
  isGenerating: boolean;
  onStopGenerating: () => void;
  settings: AppSettings;
  status: AppStatus;
  developerMode: boolean;
  onExportChat: () => void;
  onClearChat: () => void;
  onToggleMic?: (active: boolean) => void;
  isMicOpen?: boolean;
}

const StatusDot = ({ status }: { status: AppStatus }) => {
  const colorMap: Record<AppStatus, string> = {
    online: "bg-status-online",
    generating: "bg-status-generating",
    error: "bg-status-error",
    loading: "bg-status-generating",
  };
  return (
    <span className={`inline-block w-1.5 h-1.5 rounded-full ${colorMap[status]}`} />
  );
};

const SystemBar = ({ settings, status }: { settings: AppSettings; status: AppStatus }) => (
  <div className="flex items-center gap-4 px-4 md:px-8 h-8 bg-system-bar text-[11px] text-muted-foreground border-b border-border overflow-x-auto whitespace-nowrap">
    <span className="flex items-center gap-1.5">
      <StatusDot status={status} />
      {status === "generating" ? "Generating" : status === "error" ? "Error" : "Online"}
    </span>
    <span>Model: {settings.model}</span>
    <span>Context: {settings.contextWindow}</span>
    <span>Temp: {settings.temperature}</span>
    {settings.ragEnabled && <span>📚 RAG</span>}
    {settings.asrEnabled && <span>🎤 ASR</span>}
    {settings.ttsEnabled && <span>🔊 TTS</span>}
    {settings.streamResponses && <span>Stream: On</span>}
  </div>
);

const CodeBlock = ({ children, className }: { children: string; className?: string }) => {
  const [copied, setCopied] = useState(false);
  const language = className?.replace("language-", "") || "";

  const handleCopy = () => {
    navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group">
      <div className="flex items-center justify-between bg-secondary px-4 py-1.5 rounded-t-md text-[11px] text-muted-foreground">
        <span>{language || "code"}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 hover:text-foreground transition-colors"
        >
          {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="!mt-0 !rounded-t-none">
        <code className={className}>{children}</code>
      </pre>
    </div>
  );
};

const MessageActions = ({
  message,
  onCopy,
  onRegenerate,
  onDelete,
  developerMode,
}: {
  message: Message;
  onCopy: () => void;
  onRegenerate?: () => void;
  onDelete: () => void;
  developerMode: boolean;
}) => {
  const [copied, setCopied] = useState(false);
  const [showMeta, setShowMeta] = useState(false);

  const handleCopy = () => {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
      <button
        onClick={handleCopy}
        className="flex items-center gap-1 px-2 py-1 text-[11px] text-muted-foreground hover:text-foreground rounded transition-colors"
      >
        {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
        {copied ? "Copied" : "Copy"}
      </button>
      {onRegenerate && (
        <button
          onClick={onRegenerate}
          className="flex items-center gap-1 px-2 py-1 text-[11px] text-muted-foreground hover:text-foreground rounded transition-colors"
        >
          <RefreshCw className="w-3 h-3" /> Regenerate
        </button>
      )}
      <button
        onClick={onDelete}
        className="flex items-center gap-1 px-2 py-1 text-[11px] text-muted-foreground hover:text-destructive rounded transition-colors"
      >
        <Trash2 className="w-3 h-3" />
      </button>

      {/* Metadata on hover */}
      <div className="relative ml-2">
        <button
          onMouseEnter={() => setShowMeta(true)}
          onMouseLeave={() => setShowMeta(false)}
          className="p-1 text-muted-foreground hover:text-foreground rounded transition-colors"
        >
          <Clock className="w-3 h-3" />
        </button>
        {showMeta && (
          <div className="absolute bottom-full left-0 mb-1 bg-secondary border border-border rounded-md px-3 py-2 text-[11px] text-muted-foreground whitespace-nowrap z-10 shadow-lg">
            <p>{new Date(message.timestamp).toLocaleString()}</p>
            {developerMode && message.tokenCount && (
              <p className="flex items-center gap-1 mt-0.5">
                <Hash className="w-3 h-3" /> {message.tokenCount} tokens
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const ChatArea = ({
  messages,
  onSendMessage,
  onToggleSidebar,
  onDeleteMessage,
  onRegenerateMessage,
  isGenerating,
  onStopGenerating,
  settings,
  status,
  developerMode,
  onExportChat,
  onClearChat,
  onToggleMic,
  isMicOpen,
}: ChatAreaProps) => {
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [attachments, setAttachments] = useState<File[]>([]);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  // Play audio when Jarvis speaks
  useEffect(() => {
    const lastMsg = messages[messages.length - 1];
    if (lastMsg?.role === "assistant" && (lastMsg as any).audio) {
      console.log("🔊 Audio received from Jarvis, playing...");
      const audioData = (lastMsg as any).audio;
      
      // Decode base64 to blob
      const byteCharacters = atob(audioData);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const audioBlob = new Blob([byteArray], { type: 'audio/wav' });
      const url = URL.createObjectURL(audioBlob);
      
      if (audioPlayerRef.current) {
        audioPlayerRef.current.src = url;
        audioPlayerRef.current.volume = 1.0;
        audioPlayerRef.current.play().catch(e => {
          console.error("❌ Audio playback failed:", e);
          toast.error("Audio playback failed. Please check browser permissions.");
        });
      }
    }
  }, [messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [input]);

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleScroll = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    setShowScrollBtn(distanceFromBottom > 100);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    onToggleMic?.(false);
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
  }, [onToggleMic]);

  const toggleVoiceChat = async (forceActive?: boolean) => {
    const shouldStop = forceActive === false || (forceActive === undefined && isRecording);
    
    if (shouldStop) {
      stopRecording();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      // VAD / Silence Detection Logic
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);

      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      let lastSpeakTime = Date.now();

      const checkSilence = () => {
        if (mediaRecorderRef.current?.state !== "recording") return;
        
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) sum += dataArray[i];
        const average = sum / bufferLength;

        if (average > 10) {
          lastSpeakTime = Date.now();
        } else {
          const silenceDuration = Date.now() - lastSpeakTime;
          if (silenceDuration > 1000) { 
            console.log("🤫 Silence detected, stopping...");
            stopRecording();
            return;
          }
        }
        
        requestAnimationFrame(checkSilence);
      };

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        if (audioBlob.size < 1000) {
          toast.error("Audio too short.");
          return;
        }

        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');

        toast.info("Transcribing...");
        try {
          const res = await axios.post('/api/audio/transcribe', formData);
          const text = res.data.text?.trim();
          
          if (text && text.length > 0) {
            console.log("📝 Transcribed:", text);
            setInput(text); // Paste into input box
            
            // Short delay to let user see it, then send
            setTimeout(() => {
              onSendMessage(text, true); 
              setInput(""); 
              toast.success("Thinking...");
            }, 500);
          } else {
            toast.error("Could not understand audio.");
          }
        } catch (e) {
          toast.error("Transcription failed.");
        }
        
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
      };

      recorder.start();
      setIsRecording(true);
      onToggleMic?.(true);
      toast.success("Listening...");
      
      requestAnimationFrame(checkSilence);

    } catch (e) {
      toast.error("Microphone access denied.");
    }
  };

  useEffect(() => {
    if (isMicOpen !== undefined && isMicOpen !== isRecording) {
      toggleVoiceChat(isMicOpen);
    }
  }, [isMicOpen]);

  const handleSubmit = () => {
    if ((!input.trim() && attachments.length === 0) || isGenerating) return;
    
    if (attachments.length > 0) {
      toast.info(`Uploading ${attachments.length} files...`);
    }
    
    onSendMessage(input.trim(), false); 
    setInput("");
    setAttachments([]);
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachments((prev) => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
    if (e.key === "Enter" && e.ctrlKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const lastAssistantIdx = (() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === "assistant") return i;
    }
    return -1;
  })();

  return (
    <div className="flex-1 flex flex-col h-screen min-w-0">
      <audio ref={audioPlayerRef} className="hidden" />
      
      {/* Top bar */}
      <div className="flex items-center justify-between h-12 px-4 border-b border-border">
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-1.5 rounded hover:bg-accent text-muted-foreground"
          >
            <Menu className="w-5 h-5" />
          </button>
          <span className="text-sm text-muted-foreground">JARVIS</span>
        </div>
        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <>
              <button
                onClick={onExportChat}
                className="p-1.5 rounded hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
                title="Export conversation"
              >
                <Download className="w-4 h-4" />
              </button>
              <button
                onClick={() => setShowClearConfirm(true)}
                className="p-1.5 rounded hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
                title="Clear conversation"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* System bar */}
      <SystemBar settings={settings} status={status} />

      {/* Messages */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto relative"
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-2">
              <h2 className="text-lg font-medium text-foreground">How can I help you today?</h2>
              <p className="text-sm text-muted-foreground">Start a conversation with JARVIS</p>
            </div>
          </div>
        ) : (
          <div>
            {messages.map((msg, idx) => (
              <div
                key={msg.id}
                className={`group animate-fade-in ${
                  msg.role === "assistant" ? "bg-ai-message" : ""
                }`}
              >
                <div className="max-w-[800px] mx-auto px-4 py-5 md:px-8">
                  <div className="flex gap-4">
                    <div
                      className={`w-7 h-7 rounded-sm flex items-center justify-center text-xs font-medium flex-shrink-0 ${
                        msg.role === "assistant"
                          ? "bg-emerald-600 text-foreground"
                          : "bg-primary text-foreground"
                      }`}
                    >
                      {msg.role === "assistant" ? "J" : "U"}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div
                        className={`markdown-body text-[15px] leading-[1.7] text-foreground ${
                          isGenerating && idx === lastAssistantIdx ? "streaming-cursor" : ""
                        }`}
                      >
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code({ className, children, ...props }) {
                              const isBlock = className?.startsWith("language-");
                              if (isBlock) {
                                return (
                                  <CodeBlock className={className}>
                                    {String(children).replace(/\n$/, "")}
                                  </CodeBlock>
                                );
                              }
                              return <code className={className} {...props}>{children}</code>;
                            },
                            pre({ children }) {
                              return <>{children}</>;
                            },
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                      <MessageActions
                        message={msg}
                        onCopy={() => navigator.clipboard.writeText(msg.content)}
                        onRegenerate={
                          msg.role === "assistant"
                            ? () => onRegenerateMessage(msg.id)
                            : undefined
                        }
                        onDelete={() => onDeleteMessage(msg.id)}
                        developerMode={developerMode}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Scroll to bottom */}
        {showScrollBtn && (
          <button
            onClick={scrollToBottom}
            className="sticky bottom-4 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-primary border border-border flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors shadow-md z-10 mx-auto"
          >
            <ArrowDown className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Stop generating */}
      {isGenerating && (
        <div className="flex justify-center py-2">
          <button
            onClick={onStopGenerating}
            className="flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground border border-border rounded-md hover:bg-accent transition-colors"
          >
            <Square className="w-3 h-3" /> Stop generating
          </button>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-border p-4">
        <div className="max-w-[800px] mx-auto space-y-3">
          {/* File Previews */}
          {attachments.length > 0 && (
            <div className="flex flex-wrap gap-2 pb-2">
              {attachments.map((file, i) => (
                <div key={i} className="relative group bg-secondary border border-border rounded-md px-3 py-2 flex items-center gap-2 max-w-[200px]">
                  {file.type.startsWith('image/') ? <ImageIcon className="w-3.5 h-3.5" /> : <FileText className="w-3.5 h-3.5" />}
                  <span className="text-xs truncate">{file.name}</span>
                  <button 
                    onClick={() => removeAttachment(i)}
                    className="absolute -top-1.5 -right-1.5 bg-background border border-border rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="relative flex items-end rounded-lg border border-[hsl(var(--input-border))] bg-input">
            <div className="flex items-center p-1.5 gap-0.5">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                title="Attach file"
              >
                <Paperclip className="w-4 h-4" />
              </button>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                multiple
                onChange={handleFileChange}
              />
            </div>

            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isRecording ? "Listening..." : "Send a message..."}
              rows={1}
              disabled={isGenerating}
              className="flex-1 resize-none bg-transparent text-foreground text-[15px] placeholder:text-muted-foreground px-2 py-3 focus:outline-none disabled:opacity-50"
            />

            <div className="flex items-center p-1.5 gap-0.5">
              <button
                onClick={() => toggleVoiceChat()}
                className={`p-2 rounded-md transition-colors ${
                  isRecording 
                    ? "text-emerald-500 bg-emerald-500/10 hover:bg-emerald-500/20" 
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
                title={isRecording ? "Stop recording" : "Voice chat"}
              >
                {isRecording ? <Mic className="w-4 h-4 animate-pulse" /> : <Mic className="w-4 h-4" />}
              </button>
              <button
                onClick={handleSubmit}
                disabled={(!input.trim() && attachments.length === 0) || isGenerating}
                className="p-2 rounded-md text-emerald-600 hover:text-emerald-500 hover:bg-emerald-500/10 disabled:opacity-30 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
          <p className="text-[11px] text-muted-foreground text-center mt-2">
            JARVIS may produce inaccurate information. Shift+Enter for new line.
          </p>
        </div>
      </div>

      {/* Clear confirmation modal */}
      {showClearConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-secondary border border-border rounded-lg p-6 max-w-sm mx-4 space-y-4">
            <h3 className="text-sm font-medium text-foreground">Clear conversation?</h3>
            <p className="text-sm text-muted-foreground">This will delete all messages in this conversation.</p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowClearConfirm(false)}
                className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onClearChat();
                  setShowClearConfirm(false);
                }}
                className="px-3 py-1.5 text-sm bg-destructive text-foreground rounded-md hover:opacity-90 transition-colors"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatArea;
