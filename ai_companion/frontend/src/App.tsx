import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Brain, Cpu, Mic, Volume2, Settings, BarChart3, Zap, Clock, AlertCircle } from 'lucide-react';

interface SystemStatus {
  interactions: number;
  confidence: number;
  stability: number;
  active_philosopher: string;
  response_time_ms: number;
  merkle_root: string;
}

interface AudioDiagnostics {
  cochlear_status: 'active' | 'idle' | 'error';
  pom_status: 'active' | 'idle' | 'error';
  corrections_applied: number;
  voice_adaptations: number;
  speaker_profiles: number;
  phoneme_mastery: { [key: string]: number };
}

interface Message {
  id: string;
  sender: 'user' | 'kaygee';
  text: string;
  timestamp: number;
}

interface EventLog {
  timestamp: number;
  level: 'info' | 'warning' | 'error' | 'success';
  message: string;
}

interface SpaceFieldMetrics {
  levels: number;
  sides: number;
  alpha: number;
  rotation: number;
  low_freq_energy: number;
  high_freq_energy: number;
  fractal_estimate: number;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState<SystemStatus>({
    interactions: 0,
    confidence: 0.75,
    stability: 0.88,
    active_philosopher: 'Kant',
    response_time_ms: 145,
    merkle_root: '0x...'
  });
  const [audioDiagnostics, setAudioDiagnostics] = useState<AudioDiagnostics>({
    cochlear_status: 'idle',
    pom_status: 'idle',
    corrections_applied: 0,
    voice_adaptations: 0,
    speaker_profiles: 1,
    phoneme_mastery: {}
  });
  const [eventLog, setEventLog] = useState<EventLog[]>([]);
  const [config, setConfig] = useState({
    learning_enabled: true,
    corrections_enabled: true,
    plasticity_enabled: true,
    voice_adaptation: true,
    cpu_threads: 4,
    learning_rate: 0.01,
    attention_threshold: 0.6
  });
  const [spaceFieldMetrics, setSpaceFieldMetrics] = useState<SpaceFieldMetrics>({
    levels: 3,
    sides: 4,
    alpha: 0.75,
    rotation: 0,
    low_freq_energy: 0,
    high_freq_energy: 0,
    fractal_estimate: 0
  });

  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isListening, setIsListening] = useState(false);

  // WebSocket connection
  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');
    
    websocket.onopen = () => {
      addLog('success', 'Connected to KayGee backend');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'status_update') {
          setStatus(data.data);
        } else if (data.type === 'message') {
          const newMessage: Message = {
            id: Date.now().toString(),
            sender: 'kaygee',
            text: data.text,
            timestamp: Date.now()
          };
          setMessages(prev => [...prev, newMessage]);
          addLog('info', 'Response received');
        } else if (data.type === 'audio_diagnostics') {
          setAudioDiagnostics(data.data);
        }
      } catch (e) {
        console.error('WebSocket message error:', e);
      }
    };

    websocket.onerror = () => {
      addLog('error', 'WebSocket connection error');
    };

    websocket.onclose = () => {
      addLog('warning', 'Disconnected from backend');
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, []);

  // Update space field based on status
  useEffect(() => {
    if (status) {
      setSpaceFieldMetrics(prev => ({
        ...prev,
        levels: Math.max(1, Math.min(5, Math.floor(status.confidence * 5))),
        sides: 4 + Math.floor(status.stability * 4),
        alpha: status.confidence,
        rotation: (Date.now() / 100) % 360
      }));
    }
  }, [status]);

  // Cognitive resonance streaming (Phase-Locked Loop Integration)
  useEffect(() => {
    const streamResonance = () => {
      if (!status) return;

      const levels = spaceFieldMetrics.levels;
      const sides = spaceFieldMetrics.sides;
      const globalAngle = (Date.now() / 1000) * 0.01;  // Matches Python rotation_speed

      // Calculate dominant frequency (JS visualizer formula)
      const dominantFreq = levels <= 1 
        ? sides 
        : Math.pow(sides, levels - 1) / Math.pow(2, levels - 2);

      // Phase coherence (PLL lock indicator)
      const phaseCoherence = Math.abs(Math.cos(globalAngle));

      // Stream to backend every 500ms
      const signature = {
        timestamp: Date.now() / 1000,
        levels,
        sides,
        dominantFreq,
        phaseCoherence,
        spectralWidth: sides * levels,
        globalAngle,
        emergentMode: true
      };

      fetch('http://localhost:8000/api/resonance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signature)
      }).catch(err => console.debug('Resonance stream failed:', err));
    };

    const interval = setInterval(streamResonance, 500);
    return () => clearInterval(interval);
  }, [status, spaceFieldMetrics]);

  const addLog = useCallback((level: EventLog['level'], message: string) => {
    setEventLog(prev => [...prev, { timestamp: Date.now(), level, message }].slice(-50));
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: input,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    addLog('info', `Sent: "${input.substring(0, 30)}..."`);

    try {
      const response = await fetch('http://localhost:8000/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input })
      });

      if (!response.ok) throw new Error('Failed to send message');
      
      const data = await response.json();
      
      if (data.response) {
        const kaygeeMessage: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'kaygee',
          text: data.response,
          timestamp: Date.now()
        };
        setMessages(prev => [...prev, kaygeeMessage]);
      }
    } catch (error) {
      addLog('error', 'Failed to communicate with backend');
      console.error(error);
    }

    setInput('');
  };

  const handleReset = async () => {
    try {
      await fetch('http://localhost:8000/reset', { method: 'POST' });
      setMessages([]);
      addLog('success', 'Session reset');
    } catch (error) {
      addLog('error', 'Reset failed');
    }
  };

  const handleConfigUpdate = async (key: string, value: any) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    
    try {
      await fetch('http://localhost:8000/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
      });
      addLog('info', `Updated ${key}: ${value}`);
    } catch (error) {
      addLog('error', 'Config update failed');
    }
  };

  return (
    <div className="h-screen bg-gray-900 text-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="w-8 h-8 text-purple-400" />
            <div>
              <h1 className="text-2xl font-bold">KayGee 1.0</h1>
              <p className="text-sm text-gray-400">Bio-Inspired Cognitive Dashboard</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${ws?.readyState === WebSocket.OPEN ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-400">
                {ws?.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - 3 Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* LEFT COLUMN - System Metrics & Controls */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          
          {/* System Status */}
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-400" />
              System Status
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Interactions:</span>
                <span className="font-mono">{status.interactions}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Confidence:</span>
                <span className="font-mono">{(status.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Stability:</span>
                <span className="font-mono">{(status.stability * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Philosopher:</span>
                <span className="font-semibold text-purple-400">{status.active_philosopher}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Response Time:</span>
                <span className="font-mono">{status.response_time_ms}ms</span>
              </div>
            </div>
          </div>

          {/* Audio Diagnostics */}
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Volume2 className="w-5 h-5 text-green-400" />
              Audio System
            </h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Cochlear:</span>
                <span className={`px-2 py-0.5 rounded text-xs ${
                  audioDiagnostics.cochlear_status === 'active' ? 'bg-green-900 text-green-200' :
                  audioDiagnostics.cochlear_status === 'idle' ? 'bg-yellow-900 text-yellow-200' :
                  'bg-red-900 text-red-200'
                }`}>
                  {audioDiagnostics.cochlear_status}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">POM:</span>
                <span className={`px-2 py-0.5 rounded text-xs ${
                  audioDiagnostics.pom_status === 'active' ? 'bg-green-900 text-green-200' :
                  audioDiagnostics.pom_status === 'idle' ? 'bg-yellow-900 text-yellow-200' :
                  'bg-red-900 text-red-200'
                }`}>
                  {audioDiagnostics.pom_status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Corrections:</span>
                <span className="font-mono">{audioDiagnostics.corrections_applied}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Voice Adaptations:</span>
                <span className="font-mono">{audioDiagnostics.voice_adaptations}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Speaker Profiles:</span>
                <span className="font-mono">{audioDiagnostics.speaker_profiles}</span>
              </div>
            </div>
          </div>

          {/* Space Field Visualization */}
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              Symbolic Cognition
            </h2>
            <div className="bg-gray-900 rounded p-2">
              <img 
                src={`http://localhost:8000/visualization/space_field/svg?sides=${spaceFieldMetrics.sides}&levels=${spaceFieldMetrics.levels}&alpha=${spaceFieldMetrics.alpha}&rotation=${spaceFieldMetrics.rotation}`}
                alt="Space Field"
                className="w-full h-48 object-contain"
              />
            </div>
            <div className="mt-2 space-y-1 text-xs text-gray-400">
              <div className="flex justify-between">
                <span>Depth:</span>
                <span className="font-mono">{spaceFieldMetrics.levels}</span>
              </div>
              <div className="flex justify-between">
                <span>Principles:</span>
                <span className="font-mono">{spaceFieldMetrics.sides}</span>
              </div>
              <div className="flex justify-between">
                <span>Fractal:</span>
                <span className="font-mono">{spaceFieldMetrics.fractal_estimate.toFixed(3)}</span>
              </div>
            </div>
          </div>

          {/* Control Toggles */}
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Settings className="w-5 h-5 text-orange-400" />
              Controls
            </h2>
            <div className="space-y-2">
              {[
                { key: 'learning_enabled', label: 'SKG Learning' },
                { key: 'corrections_enabled', label: 'Auto Corrections' },
                { key: 'plasticity_enabled', label: 'Adaptive Plasticity' },
                { key: 'voice_adaptation', label: 'Voice Adaptation' }
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm text-gray-300">{label}</span>
                  <input
                    type="checkbox"
                    checked={config[key as keyof typeof config] as boolean}
                    onChange={(e) => handleConfigUpdate(key, e.target.checked)}
                    className="w-4 h-4"
                  />
                </label>
              ))}
            </div>
            <button
              onClick={handleReset}
              className="mt-4 w-full py-2 bg-red-600 hover:bg-red-700 rounded text-sm font-semibold"
            >
              Reset Session
            </button>
          </div>

          {/* Merkle Root */}
          <div className="p-4">
            <h2 className="text-sm font-semibold mb-2 text-gray-400">Merkle Root</h2>
            <div className="bg-gray-900 rounded p-2 font-mono text-xs break-all text-green-400">
              {status.merkle_root}
            </div>
          </div>

        </div>

        {/* CENTER COLUMN - Conversation */}
        <div className="flex-1 flex flex-col bg-gray-850">
          
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <Brain className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">Start a conversation with KayGee</p>
                  <p className="text-sm mt-2">Type a message or use voice input</p>
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xl px-4 py-2 rounded-lg ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-100'
                    }`}
                  >
                    <p>{msg.text}</p>
                    <span className="text-xs opacity-70 mt-1 block">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Input */}
          <div className="border-t border-gray-700 p-4 bg-gray-800">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your message..."
                className="flex-1 bg-gray-700 text-gray-100 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => setIsListening(!isListening)}
                className={`p-2 rounded-lg ${isListening ? 'bg-red-600' : 'bg-gray-700'} hover:bg-opacity-80`}
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN - Logs & Performance */}
        <div className="w-80 bg-gray-800 border-l border-gray-700 overflow-y-auto">
          
          {/* Event Log */}
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-cyan-400" />
              Event Log
            </h2>
            <div className="space-y-1 text-xs font-mono">
              {eventLog.slice(-20).reverse().map((event, idx) => (
                <div
                  key={idx}
                  className={`p-2 rounded ${
                    event.level === 'error' ? 'bg-red-900/30 text-red-300' :
                    event.level === 'warning' ? 'bg-yellow-900/30 text-yellow-300' :
                    event.level === 'success' ? 'bg-green-900/30 text-green-300' :
                    'bg-gray-700 text-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <span className="flex-1">{event.message}</span>
                    <span className="opacity-50 whitespace-nowrap">
                      {new Date(event.timestamp).toLocaleTimeString().slice(0, 8)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              Performance
            </h2>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">CPU Threads</span>
                  <span className="font-mono">{config.cpu_threads}</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="8"
                  value={config.cpu_threads}
                  onChange={(e) => handleConfigUpdate('cpu_threads', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Learning Rate</span>
                  <span className="font-mono">{config.learning_rate.toFixed(3)}</span>
                </div>
                <input
                  type="range"
                  min="0.001"
                  max="0.1"
                  step="0.001"
                  value={config.learning_rate}
                  onChange={(e) => handleConfigUpdate('learning_rate', parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Attention</span>
                  <span className="font-mono">{config.attention_threshold.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.05"
                  value={config.attention_threshold}
                  onChange={(e) => handleConfigUpdate('attention_threshold', parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
          </div>

          {/* Phoneme Mastery (if available) */}
          {Object.keys(audioDiagnostics.phoneme_mastery).length > 0 && (
            <div className="p-4">
              <h2 className="text-sm font-semibold mb-2 text-gray-400">Phoneme Mastery</h2>
              <div className="space-y-1 text-xs">
                {Object.entries(audioDiagnostics.phoneme_mastery).slice(0, 10).map(([phoneme, score]) => (
                  <div key={phoneme} className="flex justify-between items-center">
                    <span className="font-mono text-gray-400">{phoneme}</span>
                    <div className="flex-1 mx-2 bg-gray-700 h-2 rounded overflow-hidden">
                      <div 
                        className="h-full bg-green-500" 
                        style={{ width: `${score * 100}%` }}
                      ></div>
                    </div>
                    <span className="font-mono text-gray-300">{(score * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
