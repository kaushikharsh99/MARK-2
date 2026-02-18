import { useState, useCallback, useRef, useEffect } from "react";
import axios from "axios";
import Sidebar from "@/components/Sidebar";
import ChatArea from "@/components/ChatArea";
import SettingsPanel from "@/components/SettingsPanel";
import { settingsConfig } from "@/config/settingsConfig";
import { useJarvis } from "@/hooks/useJarvis";
import type { Conversation, Message, AppSettings, AppStatus } from "@/types";
import { toast } from "sonner";

const generateId = () => Math.random().toString(36).slice(2, 10);

const generateTitle = (content: string) => {
  const trimmed = content.slice(0, 40).trim();
  return trimmed.length < content.length ? trimmed + "…" : trimmed;
};

const defaultSettings: AppSettings = {
  model: "BitNet 2B",
  temperature: 0.7,
  maxTokens: 2048,
  contextWindow: 2048,
  ragEnabled: false,
  asrEnabled: true,
  ttsEnabled: true,
  streamResponses: true,
  developerMode: false,
};

const Index = () => {
  const [activeView, setActiveView] = useState("chat");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isMicOpen, setIsMicOpen] = useState(false);
  const [settings, setSettings] = useState<AppSettings>(defaultSettings);
  
  const { 
    status, 
    specs, 
    overview, 
    providers, 
    marketplaceModels,
    sendMessage, 
    clearMemory, 
    setOnMessage, 
    loadModel, 
    installProvider,
    downloadModel
  } = useJarvis(settings);

  const activeConversation = conversations.find((c) => c.id === activeConversationId);
  const messages = activeConversation?.messages ?? [];

  // Listen for Jarvis responses
  useEffect(() => {
    setOnMessage((data: any) => {
      if (data.type === "wake_word_detected") {
        toast.success(data.text);
        setIsMicOpen(true);
        return;
      }

      if (data.sender === "Jarvis") {
        const aiMsg: Message = {
          id: generateId(),
          role: "assistant",
          content: data.text,
          timestamp: Date.now(),
          tokenCount: Math.ceil(data.text.length / 4),
        };
        
        setConversations((prev) =>
          prev.map((c) =>
            c.id === activeConversationId ? { ...c, messages: [...c.messages, aiMsg] } : c
          )
        );
        setIsGenerating(false);
      }
    });
  }, [activeConversationId, setOnMessage]);

  const createConversation = useCallback((firstMessage?: Message): string => {
    const id = generateId();
    const conv: Conversation = {
      id,
      title: firstMessage ? generateTitle(firstMessage.content) : "New Chat",
      messages: firstMessage ? [firstMessage] : [],
      pinned: false,
      createdAt: Date.now(),
    };
    setConversations((prev) => [conv, ...prev]);
    setActiveConversationId(id);
    return id;
  }, []);

  const handleNewChat = useCallback(() => {
    createConversation();
    setActiveView("chat");
  }, [createConversation]);

  const handleSendMessage = useCallback(
    (content: string, speakResponse: boolean = false) => {
      const userMsg: Message = {
        id: generateId(),
        role: "user",
        content,
        timestamp: Date.now(),
        tokenCount: Math.ceil(content.split(/\s+/).length * 1.3),
      };

      let convId = activeConversationId;

      if (!convId || !conversations.find((c) => c.id === convId)) {
        convId = createConversation(userMsg);
      } else {
        setConversations((prev) =>
          prev.map((c) =>
            c.id === convId
              ? {
                  ...c,
                  messages: [...c.messages, userMsg],
                  title: c.messages.length === 0 ? generateTitle(content) : c.title,
                }
              : c
          )
        );
      }

      setIsGenerating(true);
      sendMessage(content, speakResponse);
    },
    [activeConversationId, conversations, createConversation, sendMessage]
  );

  const handleStopGenerating = useCallback(() => {
    setIsGenerating(false);
  }, []);

  const handleDeleteMessage = useCallback(
    (msgId: string) => {
      setConversations((prev) =>
        prev.map((c) =>
          c.id === activeConversationId
            ? { ...c, messages: c.messages.filter((m) => m.id !== msgId) }
            : c
        )
      );
    },
    [activeConversationId]
  );

  const handleRegenerateMessage = useCallback(
    (msgId: string) => {
      if (!activeConversationId) return;
      const conv = conversations.find((c) => c.id === activeConversationId);
      if (!conv) return;

      const msgIdx = conv.messages.findIndex((m) => m.id === msgId);
      if (msgIdx === -1) return;

      let userMsg: Message | undefined;
      for (let i = msgIdx - 1; i >= 0; i--) {
        if (conv.messages[i].role === "user") {
          userMsg = conv.messages[i];
          break;
        }
      }

      setConversations((prev) =>
        prev.map((c) =>
          c.id === activeConversationId
            ? { ...c, messages: c.messages.filter((m) => m.id !== msgId) }
            : c
        )
      );

      if (userMsg) {
        handleSendMessage(userMsg.content);
      }
    },
    [activeConversationId, conversations, handleSendMessage]
  );

  const handleDeleteConversation = useCallback(
    (id: string) => {
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        setActiveConversationId(null);
      }
    },
    [activeConversationId]
  );

  const handleRenameConversation = useCallback((id: string, title: string) => {
    setConversations((prev) =>
      prev.map((c) => (id === c.id ? { ...c, title } : c))
    );
  }, []);

  const handlePinConversation = useCallback((id: string) => {
    setConversations((prev) =>
      prev.map((c) => (id === c.id ? { ...c, pinned: !c.pinned } : c))
    );
  }, []);

  const handleExportChat = useCallback(() => {
    if (!activeConversation) return;
    const content = activeConversation.messages
      .map((m) => `## ${m.role === "user" ? "User" : "JARVIS"}\n\n${m.content}`)
      .join("\n\n---\n\n");
    const blob = new Blob([`# ${activeConversation.title}\n\n${content}`], {
      type: "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${activeConversation.title}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }, [activeConversation]);

  const handleClearChat = useCallback(() => {
    if (!activeConversationId) return;
    clearMemory();
    setConversations((prev) =>
      prev.map((c) => (activeConversationId === c.id ? { ...c, messages: [] } : c))
    );
  }, [activeConversationId, clearMemory]);

  const toggleDeveloperMode = useCallback(() => {
    setSettings((prev) => ({ ...prev, developerMode: !prev.developerMode }));
  }, []);

  const handleSettingsChange = useCallback((newValues: any) => {
    // Sync with backend (optional for now, as persistence is being rolled back)
    axios.post("/api/config", { [activeView]: newValues })
      .catch(e => console.error("Failed to sync settings", e));
  }, [activeView]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === "n") {
        e.preventDefault();
        handleNewChat();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleNewChat]);

  const config = settingsConfig[activeView];

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        onNewChat={handleNewChat}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversationId}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={handleRenameConversation}
        onPinConversation={handlePinConversation}
        developerMode={settings.developerMode}
        onToggleDeveloperMode={toggleDeveloperMode}
        specs={specs}
        overview={overview}
        onLoadModel={loadModel}
      />
      {activeView === "chat" || !config ? (
        <ChatArea
          messages={messages}
          onSendMessage={handleSendMessage}
          onToggleSidebar={() => setSidebarOpen(true)}
          onDeleteMessage={handleDeleteMessage}
          onRegenerateMessage={handleRegenerateMessage}
          isGenerating={isGenerating}
          onStopGenerating={handleStopGenerating}
          settings={settings}
          status={status}
          developerMode={settings.developerMode}
          onExportChat={handleExportChat}
          onClearChat={handleClearChat}
          isMicOpen={isMicOpen}
          onToggleMic={setIsMicOpen}
        />
      ) : (
        <SettingsPanel
          title={config.title}
          fields={config.fields}
          onToggleSidebar={() => setSidebarOpen(true)}
          providers={providers}
          marketplaceModels={marketplaceModels}
          onInstallProvider={installProvider}
          onDownloadModel={downloadModel}
          onChange={handleSettingsChange}
        />
      )}
    </div>
  );
};

export default Index;
