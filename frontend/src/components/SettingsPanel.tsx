import { useState, useEffect } from "react";
import { ChevronDown, ChevronRight, Menu, ShieldAlert, Search, Download, Check, Sparkles, Box } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";

interface FieldConfig {
  label: string;
  type: "text" | "select" | "slider" | "toggle";
  description?: string;
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
  defaultValue?: string | number | boolean;
  advanced?: boolean;
}

interface SettingsPanelProps {
  title: string;
  fields: FieldConfig[];
  onToggleSidebar?: () => void;
  providers?: Record<string, { installed: boolean; version: string | null; models: string[] }>;
  marketplaceModels?: Record<string, Array<{ name: string; size: string; description: string; url?: string }>>;
  onInstallProvider?: (provider: string, password?: string) => Promise<{ status: string; message: string }>;
  onDownloadModel?: (provider: string, modelName: string, url?: string) => Promise<{ status: string; message: string }>;
  onChange?: (values: Record<string, string | number | boolean>) => void;
}

const STORAGE_KEY = "jarvis-settings";

const SettingsPanel = ({ title, fields, onToggleSidebar, providers, marketplaceModels, onInstallProvider, onDownloadModel, onChange }: SettingsPanelProps) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [installing, setInstalling] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [sudoPassword, setSudoPassword] = useState("");
  const [targetProvider, setTargetProvider] = useState<string | null>(null);
  
  const handleInstallClick = (provider: string) => {
    setTargetProvider(provider);
    setShowPasswordDialog(true);
  };

  const performInstallation = async () => {
    if (!targetProvider || !onInstallProvider) return;
    
    setInstalling(targetProvider);
    setShowPasswordDialog(false);
    
    const result = await onInstallProvider(targetProvider, sudoPassword);
    
    if (result.status === "success") {
      toast.success(result.message);
    } else {
      toast.error(result.message);
    }
    
    setInstalling(null);
    setSudoPassword("");
    setTargetProvider(null);
  };

  const [values, setValues] = useState<Record<string, string | number | boolean>>(() => {
    try {
      const stored = localStorage.getItem(`${STORAGE_KEY}-${title}`);
      if (stored) return JSON.parse(stored);
    } catch {}
    const initial: Record<string, string | number | boolean> = {};
    fields.forEach((f) => {
      if (f.defaultValue !== undefined) initial[f.label] = f.defaultValue;
    });
    return initial;
  });

  useEffect(() => {
    try {
      localStorage.setItem(`${STORAGE_KEY}-${title}`, JSON.stringify(values));
      if (onChange) onChange(values);
    } catch {}
  }, [values, title, onChange]);

  const activeProviderKey = title === "LLM Settings" ? "Model Provider" : (title === "ASR Settings" ? "ASR Provider" : "TTS Provider");
  const activeProvider = values[activeProviderKey] as string;
  const currentModel = values["Model"] as string;
  const modelsInMarket = marketplaceModels?.[activeProvider] || [];
  const filteredMarketModels = modelsInMarket.filter(m => 
    m.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    m.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    const provider = activeProvider;
    const currentModelVal = values["Model"] as string;
    
    if (provider && providers && providers[provider]?.models?.length > 0) {
      const availableModels = providers[provider].models;
      if (!availableModels.includes(currentModelVal)) {
        updateValue("Model", availableModels[0]);
      }
    }
  }, [activeProvider, providers]);

  const updateValue = (label: string, value: string | number | boolean) => {
    setValues((prev) => ({ ...prev, [label]: value }));
  };

  const basicFields = fields.filter((f) => !f.advanced);
  const advancedFields = fields.filter((f) => f.advanced);

  const renderField = (field: FieldConfig) => {
    let val = values[field.label] ?? field.defaultValue ?? "";
    let options = field.options;
    const isBitNet = values["Model Provider"] === "BitNet";
    const isDisabled = isBitNet && ["Temperature", "Max Tokens", "Context Window", "CPU Threads", "GPU Layers", "Top P", "Frequency Penalty"].includes(field.label);

    if (field.label === "Model" && activeProvider && providers) {
      const providerName = activeProvider;
      if (providers[providerName]?.models?.length > 0) {
        options = providers[providerName].models;
        if (!options.includes(val as string)) {
          val = options[0];
        }
      }
    }

    return (
      <div key={field.label} className="space-y-1.5">
        <label className="text-sm text-foreground font-medium">{field.label}</label>
        {field.description && (
          <p className="text-[12px] text-muted-foreground leading-relaxed">{field.description}</p>
        )}

        {field.type === "text" && (
          <input
            type="text"
            value={val as string}
            onChange={(e) => updateValue(field.label, e.target.value)}
            disabled={isDisabled}
            className="w-full bg-input text-foreground text-sm px-3 py-2 rounded-md border border-transparent focus:border-[hsl(var(--input-border))] focus:outline-none transition-colors disabled:opacity-50"
          />
        )}

        {field.type === "select" && (
          <div className="space-y-2">
            <select
              value={val as string}
              onChange={(e) => updateValue(field.label, e.target.value)}
              disabled={isDisabled && field.label !== "Model Provider" && field.label !== "Model"}
              className="w-full bg-input text-foreground text-sm px-3 py-2 rounded-md border border-transparent focus:border-[hsl(var(--input-border))] focus:outline-none transition-colors appearance-none cursor-pointer disabled:opacity-50"
            >
              {options?.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
            
            {["Model Provider", "ASR Provider", "TTS Provider"].includes(field.label) && providers && providers[val as string] !== undefined && (
              <div className="flex items-center justify-between px-1">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${providers[val as string].installed ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                  <span className="text-xs text-muted-foreground">
                    {providers[val as string].installed ? 'Installed' : 'Not detected'}
                  </span>
                </div>
                {!providers[val as string].installed && onInstallProvider && (
                  <button
                    onClick={() => handleInstallClick(val as string)}
                    disabled={installing === val}
                    className="text-xs font-medium text-emerald-600 hover:text-emerald-500 disabled:opacity-50 transition-colors"
                  >
                    {installing === val ? 'Installing...' : 'One-click Install'}
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {field.type === "slider" && (
          <div className={`flex items-center gap-3 ${isDisabled ? "opacity-50 pointer-events-none" : ""}`}>
            <input
              type="range"
              min={field.min ?? 0}
              max={field.max ?? 1}
              step={field.step ?? 0.1}
              value={val as number}
              onChange={(e) => updateValue(field.label, parseFloat(e.target.value))}
              disabled={isDisabled}
              className="flex-1 h-1"
            />
            <span className="text-xs text-muted-foreground w-12 text-right font-mono">{val}</span>
          </div>
        )}

        {field.type === "toggle" && (
          <button
            onClick={() => updateValue(field.label, !val)}
            className={`relative w-10 h-5 rounded-full transition-colors ${
              val ? "bg-emerald-600" : "bg-muted"
            }`}
            role="switch"
            aria-checked={!!val}
            aria-label={field.label}
          >
            <span
              className={`absolute top-0.5 w-4 h-4 rounded-full bg-foreground transition-transform ${
                val ? "left-5" : "left-0.5"
              }`}
            />
          </button>
        )}
      </div>
    );
  };

  const isMarketEnabled = title === "LLM Settings" || title === "ASR Settings" || title === "TTS Settings";

  return (
    <div className="flex-1 flex flex-col h-screen min-w-0">
      <div className="flex items-center h-12 px-4 md:px-6 border-b border-border gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-1.5 rounded hover:bg-accent text-muted-foreground"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <span className="text-sm font-medium text-foreground">{title}</span>
      </div>
      
      <div className="flex-1 flex overflow-hidden">
        {/* Left Side: Settings Fields */}
        <div className={`flex-1 overflow-y-auto p-4 md:p-6 border-r border-border transition-all ${isMarketEnabled ? "max-w-md" : "w-full"}`}>
          <div className="space-y-4">
            {basicFields.map(renderField)}

            {advancedFields.length > 0 && (
              <div className="pt-4 border-t border-border">
                <button
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showAdvanced ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                  Advanced Settings
                </button>
                {showAdvanced && (
                  <div className="mt-4 space-y-4 animate-fade-in">
                    {advancedFields.map(renderField)}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Model Marketplace */}
        {isMarketEnabled && (
          <div className="flex-[1.5] flex flex-col bg-muted/30">
            <div className="p-4 border-b border-border bg-background/50 backdrop-blur-sm">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input 
                  placeholder="Search models..." 
                  className="pl-9 h-9"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                <Sparkles className="w-3.5 h-3.5" />
                Popular {activeProvider} Models
              </div>

              {filteredMarketModels.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
                  <Box className="w-8 h-8 mb-2 opacity-20" />
                  <p className="text-sm">No models found matching "{searchQuery}"</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-3">
                  {filteredMarketModels.map((model) => {
                    const isInstalled = providers?.[activeProvider]?.models?.some(m => 
                      m.includes(model.name) || model.name.includes(m)
                    );
                    const isActive = currentModel === model.name || (isInstalled && currentModel.includes(model.name));

                    return (
                      <div 
                        key={model.name} 
                        className={`group p-4 rounded-xl border transition-all duration-200 ${
                          isActive 
                            ? "bg-background border-emerald-500/50 shadow-md shadow-emerald-500/5" 
                            : "bg-background/50 border-border hover:border-foreground/20"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="space-y-1 flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <h4 className="font-semibold text-sm truncate">{model.name}</h4>
                              <Badge variant="secondary" className="text-[10px] h-4 px-1.5 font-mono">
                                {model.size}
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                              {model.description}
                            </p>
                          </div>

                          <div className="flex flex-col gap-2">
                            {isInstalled ? (
                              <Button
                                size="sm"
                                variant={isActive ? "default" : "outline"}
                                className={`h-8 px-4 ${isActive ? "bg-emerald-600 hover:bg-emerald-600 cursor-default" : ""}`}
                                onClick={() => !isActive && updateValue("Model", model.name)}
                              >
                                {isActive ? (
                                  <><Check className="w-3.5 h-3.5 mr-1.5" /> Active</>
                                ) : (
                                  "Use Model"
                                )}
                              </Button>
                            ) : (
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-8 px-4 border-emerald-500/50 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/30"
                                onClick={async () => {
                                  setDownloading(model.name);
                                  const res = await onDownloadModel?.(activeProvider, model.name, model.url);
                                  if (res?.status === "success") toast.success(res.message);
                                  else toast.error(res?.message || "Download failed");
                                  setDownloading(null);
                                }}
                                disabled={downloading === model.name}
                              >
                                {downloading === model.name ? (
                                  "Downloading..."
                                ) : (
                                  <><Download className="w-3.5 h-3.5 mr-1.5" /> Download</>
                                )}
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-amber-500" />
              Sudo Privileges Required
            </DialogTitle>
            <DialogDescription>
              Installing <strong>{targetProvider}</strong> requires administrator permissions. 
              Please enter your system password.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              type="password"
              placeholder="System Password"
              value={sudoPassword}
              onChange={(e) => setSudoPassword(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") performInstallation();
              }}
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPasswordDialog(false)}>
              Cancel
            </Button>
            <Button onClick={performInstallation} className="bg-emerald-600 hover:bg-emerald-500">
              Authenticate & Install
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SettingsPanel;
