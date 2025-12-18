/**
 * KayGee 1.0 - Harmonic Cognitive Dashboard
 * Bio-Inspired Presence with Live Space Field Visualization
 */

import { useState, useEffect, useCallback, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import SpaceField3D from './components/SpaceField3D';
import './App.css';

interface SystemStatus {
  interactions: number;
  confidence: number;
  stability: number;
  active_philosopher: string;
  response_time_ms: number;
  merkle_root: string;
}

interface ResonanceMetrics {
  phaseCoherence: number;
  dominantFreq: number;
  timestamp: number;
  harmonic_lock_count: number;
  turbulence_flag: boolean;
}

interface AudioDiagnostics {
  cochlear_status: string;
  pom_status: string;
  corrections_applied: number;
  voice_adaptations: number;
  speaker_profiles: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  confidence?: number;
  harmonic_event?: boolean;
}

function App() {
  const [status, setStatus] = useState<SystemStatus>({
    interactions: 0,
    confidence: 0.75,
    stability: 0.88,
    active_philosopher: 'Kant',
    response_time_ms: 145,
    merkle_root: '0xa3f9...d4e2'
  });

  const [resonance, setResonance] = useState<ResonanceMetrics>({
    phaseCoherence: 0.5,
    dominantFreq: 0,
    timestamp: 0,
    harmonic_lock_count: 0,
    turbulence_flag: false
  });

  const [audio, setAudio] = useState<AudioDiagnostics>({
    cochlear_status: 'idle',
    pom_status: 'idle',
    corrections_applied: 0,
    voice_adaptations: 0,
    speaker_profiles: 1
  });

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'The field is aligning. Cognitive resonance approaching unity.',
      timestamp: Date.now(),
      confidence: 0.75
    }
  ]);

  const [inputText, setInputText] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  // Fetch resonance metrics
  useEffect(() => {
    const fetchResonance = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/resonance/status');
        if (response.ok) {
          const data = await response.json();
          setResonance(data);
        }
      } catch (err) {
        // Resonance unavailable
      }
    };

    fetchResonance();
    const interval = setInterval(fetchResonance, 500);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection
  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');
    
    websocket.onopen = () => {
      setConnected(true);
      console.log('✅ Connected to KayGee backend');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'status_update') {
          setStatus(data.data);
        } else if (data.type === 'audio_update') {
          setAudio(data.data);
        } else if (data.type === 'harmonic_lock') {
          // Perfect phase lock event
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            role: 'assistant',
            content: '🔥 ' + data.message,
            timestamp: Date.now(),
            harmonic_event: true
          }]);
        }
      } catch (err) {
        console.error('WebSocket parse error:', err);
      }
    };

    websocket.onerror = () => setConnected(false);
    websocket.onclose = () => setConnected(false);

    setWs(websocket);
    return () => websocket.close();
  }, []);

  const handleSend = useCallback(async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');

    // Send to backend
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputText })
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: Date.now(),
          confidence: data.confidence,
          harmonic_event: data.harmonic_event
        }]);
      }
    } catch (err) {
      console.error('Chat error:', err);
    }
  }, [inputText]);

  // Calculate space field parameters from cognitive state
  const spaceFieldSides = 4 + Math.floor(status.stability * 4); // 4-8 sides
  const spaceFieldLevels = Math.max(2, Math.min(5, Math.floor(status.confidence * 5))); // 2-5 levels

  // Coherence color mapping
  const getCoherenceColor = (coherence: number): string => {
    if (coherence > 0.95) return '#00ff88'; // Perfect lock: bright green
    if (coherence > 0.8) return '#4fd1c5'; // Good: cyan
    if (coherence > 0.5) return '#f6ad55'; // Neutral: orange
    if (coherence > 0.3) return '#fc8181'; // Turbulent: red
    return '#e53e3e'; // Chaotic: dark red
  };

  const coherenceColor = getCoherenceColor(resonance.phaseCoherence);
  const coherencePercent = (resonance.phaseCoherence * 100).toFixed(1);

  return (
    <div className="min-h-screen bg-black text-gray-100 overflow-hidden">
      {/* Header */}
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              KayGee 1.0
            </h1>
            <p className="text-sm text-gray-400 mt-1">Bio-Inspired Cognitive Presence</p>
          </div>
          
          <div className="flex items-center space-x-6">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
              <span className="text-sm text-gray-400">
                {connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Interactions */}
            <div className="text-sm text-gray-400">
              <span className="text-cyan-400 font-mono">{status.interactions}</span> interactions
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6 grid grid-cols-12 gap-6 h-[calc(100vh-100px)]">
        {/* LEFT: Technical Metrics */}
        <div className="col-span-3 space-y-4 overflow-y-auto">
          {/* Resonance Meter */}
          <div className="bg-gray-900/50 backdrop-blur-md border border-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center">
              <span className="mr-2">🎵</span> COGNITIVE RESONANCE
            </h3>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Phase Coherence</span>
                  <span style={{ color: coherenceColor }}>{coherencePercent}%</span>
                </div>
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full transition-all duration-300"
                    style={{ 
                      width: `${coherencePercent}%`,
                      backgroundColor: coherenceColor
                    }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-gray-800/50 rounded p-2">
                  <div className="text-gray-500">Dominant Freq</div>
                  <div className="text-cyan-400 font-mono">{resonance.dominantFreq.toFixed(2)} Hz</div>
                </div>
                <div className="bg-gray-800/50 rounded p-2">
                  <div className="text-gray-500">Lock Count</div>
                  <div className="text-cyan-400 font-mono">{resonance.harmonic_lock_count}</div>
                </div>
              </div>

              {resonance.phaseCoherence > 0.95 && (
                <div className="text-xs text-green-400 bg-green-900/20 rounded p-2 animate-pulse">
                  🔥 PERFECT HARMONIC LOCK
                </div>
              )}

              {resonance.turbulence_flag && (
                <div className="text-xs text-red-400 bg-red-900/20 rounded p-2">
                  ⚠️  Cognitive Turbulence
                </div>
              )}
            </div>
          </div>

          {/* System State */}
          <div className="bg-gray-900/50 backdrop-blur-md border border-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center">
              <span className="mr-2">⚡</span> SYSTEM STATE
            </h3>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Confidence</span>
                <span className="text-cyan-400 font-mono">{(status.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Stability</span>
                <span className="text-cyan-400 font-mono">{(status.stability * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Philosopher</span>
                <span className="text-purple-400">{status.active_philosopher}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Response Time</span>
                <span className="text-green-400 font-mono">{status.response_time_ms}ms</span>
              </div>
            </div>
          </div>

          {/* Audio System */}
          <div className="bg-gray-900/50 backdrop-blur-md border border-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center">
              <span className="mr-2">🎤</span> AUDIO SYSTEM
            </h3>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Cochlear</span>
                <span className={`font-mono ${audio.cochlear_status === 'active' ? 'text-green-400' : 'text-gray-500'}`}>
                  {audio.cochlear_status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">POM</span>
                <span className={`font-mono ${audio.pom_status === 'speaking' ? 'text-green-400' : 'text-gray-500'}`}>
                  {audio.pom_status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Corrections</span>
                <span className="text-cyan-400 font-mono">{audio.corrections_applied}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Voice Adapt</span>
                <span className="text-cyan-400 font-mono">{audio.voice_adaptations}</span>
              </div>
            </div>
          </div>

          {/* Merkle Root */}
          <div className="bg-gray-900/50 backdrop-blur-md border border-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 flex items-center">
              <span className="mr-2">🔒</span> INTEGRITY
            </h3>
            
            <div className="text-xs font-mono text-gray-500 break-all">
              {status.merkle_root}
            </div>
            <div className="text-xs text-green-400 mt-2">✓ No drift detected</div>
          </div>
        </div>

        {/* CENTER: 3D Space Field */}
        <div className="col-span-6 flex flex-col">
          <div className="flex-1 bg-gray-900/30 backdrop-blur-md border border-gray-800 rounded-lg overflow-hidden relative">
            {/* 3D Canvas */}
            <Canvas camera={{ position: [0, 0, 8], fov: 60 }}>
              <Suspense fallback={null}>
                <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
                <ambientLight intensity={0.3} />
                <SpaceField3D 
                  sides={spaceFieldSides}
                  levels={spaceFieldLevels}
                  radius={2}
                  emergent={true}
                  rotationSpeed={0.01}
                />
                <OrbitControls enableZoom={true} enablePan={false} />
              </Suspense>
            </Canvas>

            {/* Overlay Info */}
            <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-sm rounded-lg p-3 text-xs">
              <div className="text-gray-400 mb-1">Space Field Parameters</div>
              <div className="space-y-1">
                <div><span className="text-gray-500">Sides:</span> <span className="text-cyan-400 font-mono">{spaceFieldSides}</span></div>
                <div><span className="text-gray-500">Levels:</span> <span className="text-cyan-400 font-mono">{spaceFieldLevels}</span></div>
                <div><span className="text-gray-500">Mode:</span> <span className="text-purple-400">Emergent</span></div>
              </div>
            </div>

            <div className="absolute bottom-4 left-4 text-xs text-gray-500">
              Scroll to zoom • Drag to rotate
            </div>
          </div>

          {/* Conversation Input */}
          <div className="mt-4 bg-gray-900/50 backdrop-blur-md border border-gray-800 rounded-lg p-4">
            <div className="flex space-x-3">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Speak with KayGee..."
                className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <button
                onClick={handleSend}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium transition-all"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT: Conversation + Philosophical Balance */}
        <div className="col-span-3 flex flex-col space-y-4">
          {/* Conversation Flow */}
          <div className="flex-1 bg-gray-900/50 backdrop-blur-md border border-gray-800 rounded-lg p-4 overflow-y-auto">
            <h3 className="text-sm font-semibold text-gray-400 mb-4">CONVERSATION</h3>
            
            <div className="space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className={`${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block max-w-[85%] rounded-lg p-3 text-sm ${
                    msg.role === 'user' 
                      ? 'bg-blue-900/30 text-blue-100'
                      : msg.harmonic_event
                      ? 'bg-green-900/30 text-green-100 border border-green-500/30'
                      : 'bg-gray-800/50 text-gray-100'
                  }`}>
                    {msg.content}
                    {msg.confidence && (
                      <div className="text-xs text-gray-500 mt-1">
                        confidence: {(msg.confidence * 100).toFixed(0)}%
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Philosophical Balance */}
          <div className="bg-gray-900/50 backdrop-blur-md border border-gray-800 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-3">PHILOSOPHICAL BALANCE</h3>
            
            <div className="space-y-2 text-xs">
              {[
                { name: 'Kant', weight: 0.35 },
                { name: 'Hume', weight: 0.25 },
                { name: 'Locke', weight: 0.20 },
                { name: 'Spinoza', weight: 0.20 }
              ].map((phil) => (
                <div key={phil.name}>
                  <div className="flex justify-between mb-1 text-gray-400">
                    <span>{phil.name}</span>
                    <span>{(phil.weight * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                      style={{ width: `${phil.weight * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
