import { useState } from "react";
import {
  MessageSquarePlus,
  Settings,
  Mic,
  Volume2,
  Database,
  Wrench,
  X,
  Pin,
  PinOff,
  Pencil,
  Trash2,
  MessageSquare,
  ChevronLeft,
  MoreHorizontal,
  Check,
  Code2,
  Cpu,
  Activity,
  Zap,
} from "lucide-react";
import type { Conversation } from "@/types";

type NavItem = {
  id: string;
  label: string;
  icon: React.ElementType;
};

const moduleItems: NavItem[] = [
  { id: "llm", label: "LLM Settings", icon: Settings },
  { id: "asr", label: "ASR Settings", icon: Mic },
  { id: "tts", label: "TTS Settings", icon: Volume2 },
  { id: "rag", label: "RAG Settings", icon: Database },
];

const systemItems: NavItem[] = [
  { id: "tools", label: "Tools", icon: Wrench },
];

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
  onNewChat: () => void;
  isOpen: boolean;
  onClose: () => void;
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onRenameConversation: (id: string, title: string) => void;
  onPinConversation: (id: string) => void;
  developerMode: boolean;
  onToggleDeveloperMode: () => void;
  specs?: any;
  overview?: any;
  onLoadModel?: () => void;
}

const SystemMonitor = ({ specs, overview, onLoadModel }: { specs: any; overview: any; onLoadModel?: () => void }) => {
  if (!specs) return null;
  
  const isRunning = overview?.llm?.status === "Running";
  const isLoading = overview?.llm?.status === "Loading";

  return (
    <div className="px-3 mb-4 space-y-3">
      <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider px-3 mb-1">Station Telemetry</p>
      <div className="bg-black/20 rounded-lg p-3 border border-border/50 space-y-2">
        <div className="flex justify-between items-center text-[10px]">
          <span className="text-muted-foreground flex items-center gap-1.5"><Cpu size={10}/> CPU</span>
          <span className="font-mono text-cyan-400">{specs.cpu?.threads} THDS</span>
        </div>
        <div className="flex justify-between items-center text-[10px]">
          <span className="text-muted-foreground flex items-center gap-1.5"><Activity size={10}/> RAM</span>
          <span className="font-mono text-blue-400">{Math.round(specs.ram?.total_gb - specs.ram?.available_gb)} GB</span>
        </div>
        {specs.gpu && (
          <div className="flex justify-between items-center text-[10px]">
            <span className="text-muted-foreground flex items-center gap-1.5"><Zap size={10}/> VRAM</span>
            <span className="font-mono text-purple-400">{specs.gpu.vram_gb} GB</span>
          </div>
        )}
        <div className="pt-2 border-t border-white/5 mt-2 space-y-2">
          <div className="flex items-center gap-2">
            <div className={`w-1 h-1 rounded-full ${isRunning ? 'bg-cyan-500 animate-pulse' : 'bg-white/10'}`} />
            <span className="text-[9px] font-bold text-white/40 uppercase tracking-tight truncate">
              {overview?.llm?.model || "ENGINE OFFLINE"}
            </span>
          </div>
          {!isRunning && onLoadModel && (
            <button 
              onClick={onLoadModel}
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-1.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-[10px] font-bold uppercase hover:bg-cyan-500 hover:text-black transition-all disabled:opacity-50"
            >
              {isLoading ? <Activity size={10} className="animate-spin"/> : <Zap size={10}/>}
              {isLoading ? "Loading..." : "Deploy Engine"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

const Sidebar = ({
  activeView,
  onViewChange,
  onNewChat,
  isOpen,
  onClose,
  conversations,
  activeConversationId,
  onSelectConversation,
  onDeleteConversation,
  onRenameConversation,
  onPinConversation,
  developerMode,
  onToggleDeveloperMode,
  specs,
  overview,
  onLoadModel,
}: SidebarProps) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);

  const pinnedChats = conversations.filter((c) => c.pinned);
  const recentChats = conversations.filter((c) => !c.pinned);

  const startRename = (conv: Conversation) => {
    setEditingId(conv.id);
    setEditTitle(conv.title);
    setMenuOpenId(null);
  };

  const confirmRename = () => {
    if (editingId && editTitle.trim()) {
      onRenameConversation(editingId, editTitle.trim());
    }
    setEditingId(null);
  };

  const renderConversation = (conv: Conversation) => {
    const isActive = conv.id === activeConversationId && activeView === "chat";
    const isEditing = editingId === conv.id;

    return (
      <div
        key={conv.id}
        className={`group relative flex items-center rounded-md transition-colors ${
          isActive
            ? "bg-accent text-foreground"
            : "text-sidebar-foreground hover:bg-accent"
        }`}
      >
        {isActive && (
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-[hsl(var(--active-indicator))] rounded-r" />
        )}

        {isEditing ? (
          <div className="flex items-center w-full px-3 py-2 gap-2">
            <input
              autoFocus
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") confirmRename();
                if (e.key === "Escape") setEditingId(null);
              }}
              className="flex-1 bg-input text-foreground text-sm px-2 py-0.5 rounded border border-[hsl(var(--input-border))] focus:outline-none min-w-0"
            />
            <button onClick={confirmRename} className="text-muted-foreground hover:text-foreground">
              <Check className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => {
              onSelectConversation(conv.id);
              onViewChange("chat");
            }}
            className="flex-1 flex items-center gap-2.5 px-3 py-2 text-sm text-left min-w-0"
          >
            <MessageSquare className="w-3.5 h-3.5 flex-shrink-0 opacity-50" />
            <span className="truncate">{conv.title}</span>
          </button>
        )}

        {!isEditing && (
          <div className="flex items-center pr-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setMenuOpenId(menuOpenId === conv.id ? null : conv.id);
              }}
              className="p-1 rounded hover:bg-[hsl(var(--hover-bg))] text-muted-foreground"
            >
              <MoreHorizontal className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {menuOpenId === conv.id && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setMenuOpenId(null)} />
            <div className="absolute right-0 top-full z-20 bg-secondary border border-border rounded-md shadow-lg py-1 min-w-[140px]">
              <button
                onClick={() => startRename(conv)}
                className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-sidebar-foreground hover:bg-accent"
              >
                <Pencil className="w-3 h-3" /> Rename
              </button>
              <button
                onClick={() => {
                  onPinConversation(conv.id);
                  setMenuOpenId(null);
                }}
                className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-sidebar-foreground hover:bg-accent"
              >
                {conv.pinned ? <PinOff className="w-3 h-3" /> : <Pin className="w-3 h-3" />}
                {conv.pinned ? "Unpin" : "Pin"}
              </button>
              <button
                onClick={() => {
                  onDeleteConversation(conv.id);
                  setMenuOpenId(null);
                }}
                className="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-destructive hover:bg-accent"
              >
                <Trash2 className="w-3 h-3" /> Delete
              </button>
            </div>
          </>
        )}
      </div>
    );
  };

  const renderNavItem = (item: NavItem) => {
    const isActive = activeView === item.id;
    return (
      <button
        key={item.id}
        onClick={() => {
          onViewChange(item.id);
          onClose();
        }}
        className={`relative w-full flex items-center gap-2.5 px-3 py-2 text-sm rounded-md transition-colors ${
          isActive
            ? "bg-accent text-foreground"
            : "text-sidebar-foreground hover:bg-accent"
        }`}
      >
        {isActive && (
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-[hsl(var(--active-indicator))] rounded-r" />
        )}
        <item.icon className="w-4 h-4" />
        {item.label}
      </button>
    );
  };

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 md:hidden" onClick={onClose} />
      )}

      <aside
        className={`fixed md:static z-50 top-0 left-0 h-full w-[260px] bg-secondary flex flex-col transition-transform duration-200 md:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 h-12">
          <span className="text-sm font-semibold text-foreground tracking-wide">JARVIS</span>
          <button onClick={onClose} className="md:hidden p-1 rounded hover:bg-accent text-muted-foreground">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* New Chat */}
        <div className="px-3 pb-3">
          <button
            onClick={() => {
              onNewChat();
              onViewChange("chat");
              onClose();
            }}
            className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-sidebar-foreground rounded-md border border-border hover:bg-accent transition-colors"
          >
            <MessageSquarePlus className="w-4 h-4" />
            New Chat
          </button>
        </div>

        {/* System Monitor */}
        <SystemMonitor specs={specs} overview={overview} onLoadModel={onLoadModel} />

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col px-3 gap-4">
          <div className="shrink-0 space-y-4">
            <div>
              <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider px-3 mb-1">Modules</p>
              <div className="space-y-0.5">{moduleItems.map(renderNavItem)}</div>
            </div>

            <div>
              <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider px-3 mb-1">System</p>
              <div className="space-y-0.5">{systemItems.map(renderNavItem)}</div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto min-h-0 space-y-4 pr-1">
            {pinnedChats.length > 0 && (
              <div>
                <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider px-3 mb-1">Pinned</p>
                <div className="space-y-0.5">{pinnedChats.map(renderConversation)}</div>
              </div>
            )}

            {recentChats.length > 0 && (
              <div>
                <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider px-3 mb-1">Recent Chats</p>
                <div className="space-y-0.5">{recentChats.map(renderConversation)}</div>
              </div>
            )}
          </div>
        </div>

        {/* Bottom */}
        <div className="px-3 py-3 border-t border-border space-y-0.5">
          <button
            onClick={onToggleDeveloperMode}
            className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm rounded-md transition-colors ${
              developerMode
                ? "bg-accent text-foreground"
                : "text-sidebar-foreground hover:bg-accent"
            }`}
          >
            <Code2 className="w-4 h-4" />
            Developer Mode
            <div
              className={`ml-auto w-7 h-4 rounded-full transition-colors flex items-center ${
                developerMode ? "bg-status-online justify-end" : "bg-muted justify-start"
              }`}
            >
              <div className="w-3 h-3 rounded-full bg-foreground mx-0.5" />
            </div>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
