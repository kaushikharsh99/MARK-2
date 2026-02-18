import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { AppSettings, AppStatus, Message } from '../types/index';

const API_BASE = "";
const WS_BASE = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}`;

export const useJarvis = (settings: AppSettings) => {
  const [status, setStatus] = useState<AppStatus>("online");
  const [specs, setSpecs] = useState<any>(null);
  const [overview, setOverview] = useState<any>(null);
  const [providers, setProviders] = useState<any>(null);
  const [marketplaceModels, setMarketplaceModels] = useState<any>(null);
  const ws = useRef<WebSocket | null>(null);
  const messageHandlerRef = useRef<((msg: any) => void) | null>(null);

  const fetchSystemData = useCallback(async () => {
    console.log("Fetching system data...");
    try {
      const [specRes, overRes, provRes, marketRes] = await Promise.all([
        axios.get(`${API_BASE}/api/system/specs`).catch(e => ({ data: null })),
        axios.get(`${API_BASE}/api/system/overview`).catch(e => ({ data: null })),
        axios.get(`${API_BASE}/api/providers`).catch(e => ({ data: null })),
        axios.get(`${API_BASE}/api/marketplace/models`).catch(e => ({ data: null }))
      ]);
      setSpecs(specRes.data);
      setOverview(overRes.data);
      setProviders(provRes.data);
      setMarketplaceModels(marketRes.data);
    } catch (e) {
      console.error("Failed to fetch system data", e);
      // Don't set status to error here to avoid blocking render if backend is down
    }
  }, []);

  const connectWS = useCallback(() => {
    console.log("Attempting to connect WebSocket...");
    if (ws.current?.readyState === WebSocket.OPEN || ws.current?.readyState === WebSocket.CONNECTING) {
      console.log("WebSocket already open or connecting");
      return;
    }

    try {
      const socket = new WebSocket(`${WS_BASE}/ws/chat`);
      
      socket.onopen = () => {
        console.log("Connected to Jarvis AI WS");
        setStatus("online");
      };

      socket.onmessage = (event) => {
        console.log("WS Message received:", event.data);
        const data = JSON.parse(event.data);
        if (messageHandlerRef.current) {
          messageHandlerRef.current(data);
        }
      };

      socket.onclose = () => {
        console.log("Disconnected from Jarvis AI WS");
        // Reconnect after delay
        setTimeout(connectWS, 5000);
      };

      socket.onerror = (err) => {
        console.error("WebSocket Error", err);
        // setStatus("error");
      };

      ws.current = socket;
    } catch (e) {
      console.error("Failed to create WebSocket", e);
    }
  }, []);

  useEffect(() => {
    console.log("useJarvis initialized");
    fetchSystemData();
    connectWS();
    const interval = setInterval(fetchSystemData, 10000); // Less frequent polling
    return () => {
      clearInterval(interval);
      if (ws.current) {
        console.log("Closing WebSocket...");
        ws.current.onclose = null; 
        ws.current.close();
      }
    };
  }, [fetchSystemData, connectWS]);

  const sendMessage = useCallback((text: string, speakResponse: boolean = false) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ text, speak_response: speakResponse }));
      return true;
    }
    console.error("Cannot send message: WebSocket is not open");
    return false;
  }, []);

  const loadModel = async () => {
    try {
      setStatus("loading");
      await axios.post(`${API_BASE}/api/model/load`);
      await fetchSystemData();
      setStatus("online");
    } catch (e) {
      setStatus("error");
    }
  };

  const clearMemory = async () => {
    try {
      await axios.post(`${API_BASE}/api/memory/clear`);
    } catch (e) {}
  };

  const installProvider = async (provider: string, password?: string) => {
    try {
      const res = await axios.post(`${API_BASE}/api/providers/install`, { provider, password });
      await fetchSystemData();
      return res.data;
    } catch (e: any) {
      console.error("Failed to install provider", e);
      return { status: "error", message: e.response?.data?.message || "Network error" };
    }
  };

  const downloadModel = async (provider: string, modelName: string, url?: string) => {
    try {
      const res = await axios.post(`${API_BASE}/api/marketplace/download`, { provider, model_name: modelName, url });
      await fetchSystemData();
      return res.data;
    } catch (e: any) {
      return { status: "error", message: "Failed to start download" };
    }
  };

  const setOnMessage = useCallback((callback: (msg: any) => void) => {
    messageHandlerRef.current = callback;
  }, []);

  return {
    status,
    specs,
    overview,
    providers,
    marketplaceModels,
    sendMessage,
    loadModel,
    clearMemory,
    installProvider,
    downloadModel,
    setOnMessage
  };
};
