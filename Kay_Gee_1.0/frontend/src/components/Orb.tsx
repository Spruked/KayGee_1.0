import React, { useEffect, useRef, useState, useCallback } from 'react';
import { PresenceStore } from '../store/presenceStore';
import { useOrbAttention } from '../hooks/useOrbAttention';
import { orbLearningGraph } from '../lib/OrbLearningGraph';
import { Box } from '@chakra-ui/react';
import * as THREE from 'three';

// Speech Recognition types (simplified)
declare global {
  interface Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }
}

// Animated Space Field component for orb center
const AnimatedSpaceField: React.FC = () => {
  const [animationFrame, setAnimationFrame] = useState(0);
  const [moodColor, setMoodColor] = useState('#00aaff'); // Bright cyan default
  const [confidence, setConfidence] = useState(0.8);
  const [rotationSpeed, setRotationSpeed] = useState(1);

  // Update based on orb state changes
  useEffect(() => {
    const handleVoiceInput = () => {
      setRotationSpeed(prev => Math.min(prev + 0.5, 3)); // Speed up on voice
      setTimeout(() => setRotationSpeed(prev => Math.max(prev - 0.2, 0.5)), 2000);
    };

    const handleApiResponse = (event: Event) => {
      const data = (event as CustomEvent).detail;
      if (data.emotion) {
        const emotion = data.emotion.toLowerCase();
        if (emotion.includes('happy') || emotion.includes('excited')) {
          setMoodColor('#00ff88'); // Brighter green
        } else if (emotion.includes('calm') || emotion.includes('focused')) {
          setMoodColor('#4488ff'); // Brighter blue
        } else if (emotion.includes('curious')) {
          setMoodColor('#ffff00'); // Bright yellow
        } else if (emotion.includes('frustrated') || emotion.includes('sad')) {
          setMoodColor('#ff4444'); // Brighter red
        } else {
          setMoodColor('#00aaff'); // Bright cyan default
        }
      }
      if (data.confidence !== undefined) {
        setConfidence(Math.max(0.3, data.confidence)); // Minimum visibility
      }
    };

    window.addEventListener('voice-input', handleVoiceInput);
    window.addEventListener('api-response', handleApiResponse);

    return () => {
      window.removeEventListener('voice-input', handleVoiceInput);
      window.removeEventListener('api-response', handleApiResponse);
    };
  }, []);

  // Animation loop
  useEffect(() => {
    const animate = () => {
      setAnimationFrame(prev => prev + rotationSpeed * 0.03); // Slightly faster base rotation
      requestAnimationFrame(animate);
    };
    const raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [rotationSpeed]);

  const generateSpaceFieldSVG = () => {
    const w = 180;
    const h = 180;
    const cx = w / 2;
    const cy = h / 2;
    const baseR = Math.min(w, h) * 0.4;

    const levels = 5;
    const sides = 8;
    const alpha = 0.444;
    const rotation = animationFrame;

    let svg = `<svg xmlns='http://www.w3.org/2000/svg' width='${w}' height='${h}' viewBox='0 0 ${w} ${h}'>`;

    // Add a subtle background glow
    svg += `<circle cx='${cx}' cy='${cy}' r='${baseR * 1.2}' fill='none' stroke='${moodColor}' stroke-width='2' stroke-opacity='0.1' />`;

    for (let level = 1; level <= levels; level++) {
      const radius = baseR * (level / levels) * (1 - (alpha - 0.1));
      const rot = rotation * (level / levels) * 0.5; // Slower rotation for each level
      const opacity = Math.max(0.15, 0.9 - level * 0.12) * confidence;

      // Add pulsing effect
      const pulse = Math.sin(animationFrame * 0.02 + level) * 0.3 + 0.7;
      const finalOpacity = opacity * pulse;

      const points: string[] = [];
      for (let i = 0; i < sides; i++) {
        const ang = (2 * Math.PI * i / sides) + rot;
        const x = cx + radius * Math.cos(ang);
        const y = cy + radius * Math.sin(ang);
        points.push(`${x},${y}`);
      }

      // More visible: filled polygons with stronger colors
      const fillColor = level === 1 ? moodColor : `rgba(${moodColor === '#00aaff' ? '0,170,255' : moodColor === '#00ff88' ? '0,255,136' : moodColor === '#4488ff' ? '68,136,255' : moodColor === '#ffff00' ? '255,255,0' : '255,68,68'}, ${finalOpacity * 0.6})`;
      svg += `<polygon points='${points.join(' ')}' fill='${fillColor}' stroke='${moodColor}' stroke-width='2' stroke-opacity='${finalOpacity}' />`;
    }

    // Add a central core
    svg += `<circle cx='${cx}' cy='${cy}' r='8' fill='${moodColor}' opacity='${confidence}' />`;

    svg += `</svg>`;
    return svg;
  };

  return (
    <Box
      dangerouslySetInnerHTML={{ __html: generateSpaceFieldSVG() }}
      width="100%"
      height="100%"
    />
  );
};

// Three.js scene for true volumetric glow
let orbMesh: THREE.Mesh | null = null;
let glowMesh: THREE.Mesh | null = null;
let glowMaterial: THREE.ShaderMaterial | null = null;

export const KayGeeOrb: React.FC = () => {
  const [presence] = useState(PresenceStore.get());
  const { targetPosition, onOrbHover } = useOrbAttention(presence.visibility === 'latent');
  const mountRef = useRef<HTMLDivElement>(null);
  const [lastCursorPosition, setLastCursorPosition] = useState({ x: 0, y: 0 });
  const [position, setPosition] = useState({ x: window.innerWidth / 2, y: window.innerHeight / 2 });
  const [isDragging, setIsDragging] = useState(false);
  const dragOffset = useRef({ x: 0, y: 0 });

  // Track cursor position for learning
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setLastCursorPosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Voice input state
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  // Allow hover interactions only when microphone interaction is active
  const [allowHover, setAllowHover] = useState(false);
  // Confidence monitoring state
  const [confidence, setConfidence] = useState(0.8);

  // Update confidence from API responses
  useEffect(() => {
    const handleApiResponse = (event: Event) => {
      const data = (event as CustomEvent).detail;
      if (data.confidence !== undefined) {
        setConfidence(Math.max(0.1, Math.min(1.0, data.confidence)));
      }
    };
    window.addEventListener('api-response', handleApiResponse);
    return () => window.removeEventListener('api-response', handleApiResponse);
  }, []);

  // Initialize voice recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onstart = () => {
        setIsListening(true);
        // Allow hover while microphone is active so the user can focus the orb
        setAllowHover(true);
        console.log('🎤 Voice recognition started');
      };

      recognitionInstance.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        console.log('🎤 Heard:', transcript);

        // Dispatch voice input event
        window.dispatchEvent(new CustomEvent('voice-input', {
          detail: {
            transcript,
            confidence: event.results[0][0].confidence,
            timestamp: Date.now()
          }
        }));

        // Also dispatch escalation with voice context
        window.dispatchEvent(new CustomEvent('user-request-escalation', {
          detail: {
            appId: 'voice-input',
            context: {
              query: transcript,
              confidence: event.results[0][0].confidence,
              type: 'voice'
            }
          }
        }));
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
        // After recognition ends, return to non-hoverable state to avoid accidental obstruction
        setAllowHover(false);
        console.log('🎤 Voice recognition ended');
      };

      recognitionInstance.onerror = (event: any) => {
        console.error('🎤 Voice recognition error:', event.error);
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }
  }, []);

  // Speech synthesis for orb responses
  const speak = useCallback((text: string) => {
    if (!voiceEnabled) return; // Skip if voice is disabled
    
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9; // Slightly slower for clarity
      utterance.pitch = 1.1; // Slightly higher pitch for friendliness
      utterance.volume = 0.7; // Not too loud

      // Use a female voice if available
      const voices = speechSynthesis.getVoices();
      const femaleVoice = voices.find(voice =>
        voice.name.toLowerCase().includes('female') ||
        voice.name.toLowerCase().includes('woman') ||
        voice.name.toLowerCase().includes('samantha') ||
        voice.name.toLowerCase().includes('victoria')
      );
      if (femaleVoice) {
        utterance.voice = femaleVoice;
      }

      // Visual feedback: brighten orb while speaking and dim after
      utterance.onstart = () => {
        try {
          if (glowMaterial && (glowMaterial as any).uniforms) (glowMaterial as any).uniforms.intensity.value = 2.2;
          if (orbMesh) {
            const mat = orbMesh.material as THREE.MeshPhysicalMaterial;
            if (mat) mat.emissiveIntensity = 2.2;
          }
          // Record speaking event for learning
          try {
            const distance = Math.sqrt(
              Math.pow(position.x - lastCursorPosition.x, 2) +
              Math.pow(position.y - lastCursorPosition.y, 2)
            );
            orbLearningGraph.recordInteraction({
              interaction: 'speak_start' as any,
              cursorPosition: lastCursorPosition,
              orbPosition: position,
              distance,
              success: true
            });
          } catch (e) {}
        } catch (e) {}
        console.log('🗣️ Orb started speaking');
      };

      utterance.onend = () => {
        try {
          if (glowMaterial && (glowMaterial as any).uniforms) (glowMaterial as any).uniforms.intensity.value = 0.35;
          if (orbMesh) {
            const mat = orbMesh.material as THREE.MeshPhysicalMaterial;
            if (mat) mat.emissiveIntensity = 0.5;
          }
          try {
            const distance = Math.sqrt(
              Math.pow(position.x - lastCursorPosition.x, 2) +
              Math.pow(position.y - lastCursorPosition.y, 2)
            );
            orbLearningGraph.recordInteraction({
              interaction: 'speak_end' as any,
              cursorPosition: lastCursorPosition,
              orbPosition: position,
              distance,
              success: true
            });
          } catch (e) {}
        } catch (e) {}
        console.log('🗣️ Orb finished speaking');
      };

      speechSynthesis.speak(utterance);
      console.log('🗣️ Orb speaking (queued):', text);
    }
  }, [voiceEnabled]);

  // Dim orb when giving user space (latent visibility), brighten otherwise
  useEffect(() => {
    try {
      if (!glowMaterial || !((glowMaterial as any).uniforms)) return;
      const intensity = presence.visibility === 'latent' ? 0.25 : 1.0;
      (glowMaterial as any).uniforms.intensity.value = intensity;
      if (orbMesh) {
        const mat = orbMesh.material as THREE.MeshPhysicalMaterial;
        if (mat) mat.emissiveIntensity = presence.visibility === 'latent' ? 0.4 : 1.0;
      }
    } catch (e) {
      // ignore
    }
  }, [presence.visibility]);

  // Map emotion to color helper
  const mapEmotionToHex = (emotion: string) => {
    const e = (emotion || '').toLowerCase();
    if (e.includes('happy') || e.includes('excited')) return 0xa0ff80;
    if (e.includes('calm') || e.includes('focused')) return 0x80c0ff;
    if (e.includes('curious')) return 0xffff80;
    if (e.includes('frustrated') || e.includes('sad')) return 0xff8080;
    return 0x00ffff;
  };

  // Animate orb/field based on API response
  const animateFromResponse = (data: any) => {
    if (!data) return;
    const resonance = (data.resonance ?? data.cognitive_resonance ?? 0.5) as number;
    const emotion = (data.emotion ?? data.mood ?? 'neutral') as string;
    const confidence = (data.confidence ?? data.stats?.confidence ?? 0.6) as number;
    const responseText = (data.response ?? data.text ?? '') as string;

    // Dispatch event for space field to react
    window.dispatchEvent(new CustomEvent('api-response', {
      detail: { emotion, confidence, resonance }
    }));

    // Speak the returned text if present
    if (responseText) {
      try { setTimeout(() => speak(responseText), 200); } catch {}
    }

    const colorHex = mapEmotionToHex(emotion);

    // Update three.js uniforms / materials
    try {
      if (glowMaterial && (glowMaterial as any).uniforms) {
        (glowMaterial as any).uniforms.intensity.value = Math.max(0.2, resonance * (1 + (confidence - 0.5)));
        (glowMaterial as any).uniforms.color.value = new THREE.Color(colorHex);
      }

      if (orbMesh) {
        const mat = orbMesh.material as THREE.MeshPhysicalMaterial;
        if (mat) {
          mat.emissive = new THREE.Color(colorHex);
          mat.emissiveIntensity = Math.min(3, resonance * 1.5 + (confidence - 0.5));
          if ((mat as any).color) (mat as any).color.set(new THREE.Color(colorHex));
        }
      }

      if (glowMesh) {
        const scale = 1 + resonance * 0.8;
        glowMesh.scale.set(scale, scale, scale);
      }
    } catch (err) {
      console.warn('Animation update error:', err);
    }
  };

  // Send text to KayGee API (POST /api/interact)
  const sendToKayGee = async (text: string) => {
    if (!text || !text.trim()) return;
    try {
      const API_BASE = (import.meta as any).env.VITE_API_URL || 'http://localhost:8001';
      const resp = await fetch(`${API_BASE}/api/interact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      if (!resp.ok) throw new Error('API not responding');
      const data = await resp.json();
      console.log('KayGee response:', data);
      animateFromResponse(data);
    } catch (err) {
      console.error('sendToKayGee error', err);
      // Soft pulse to indicate a listening state
      try {
        if (glowMaterial && (glowMaterial as any).uniforms) (glowMaterial as any).uniforms.intensity.value = 1.2;
      } catch {}
    }
  };

  // Handle voice input and generate responses (hooks into window 'voice-input' events)
  useEffect(() => {
    const handleVoiceInput = async (event: CustomEvent) => {
      const { transcript, confidence } = event.detail;
      console.log('🎤 Processing voice input:', transcript, `(${confidence * 100}%)`);

      // Send to API and animate from the returned response
      try {
        await sendToKayGee(transcript);
      } catch (err) {
        console.error('Voice input processing failed:', err);
      }
    };

    const voiceInputListener = (event: Event) => handleVoiceInput(event as CustomEvent);
    window.addEventListener('voice-input', voiceInputListener);
    return () => window.removeEventListener('voice-input', voiceInputListener);
  }, []);

  // Hook up optional global backup text input and send button IDs if present in the dashboard
  useEffect(() => {
    const input = document.getElementById('backup-text-input') as HTMLInputElement | null;
    const btn = document.getElementById('send-query-btn') as HTMLElement | null;
    if (!btn) return;

    const clickHandler = () => {
      const value = input?.value || 'Hello KayGee';
      sendToKayGee(value);
      if (input) input.value = '';
    };

    const keyHandler = (e: KeyboardEvent) => {
      if (e.key === 'Enter') clickHandler();
    };

    btn.addEventListener('click', clickHandler);
    if (input) input.addEventListener('keypress', keyHandler);

    return () => {
      btn.removeEventListener('click', clickHandler);
      if (input) input.removeEventListener('keypress', keyHandler);
    };
  }, []);

  // Animate toward target position (slower, smoother transitions)
  useEffect(() => {
    const animate = () => {
      // Don't fight user dragging
      if (!isDragging) {
        // Slower lerp for gentler motion, with a capped per-frame step
        const lerpAlpha = 0.03; // reduced from 0.09 for slower, more natural movement
        const maxStep = 100; // reduced from 200 for less aggressive tracking
        setPosition(prev => {
          const nx = prev.x + (targetPosition.x - prev.x) * lerpAlpha;
          const ny = prev.y + (targetPosition.y - prev.y) * lerpAlpha;
          const dx = nx - prev.x;
          const dy = ny - prev.y;
          const stepDist = Math.sqrt(dx * dx + dy * dy);
          if (stepDist > maxStep) {
            const scale = maxStep / stepDist;
            return { x: prev.x + dx * scale, y: prev.y + dy * scale };
          }
          return { x: nx, y: ny };
        });
      }
      requestAnimationFrame(animate);
    };
    const raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [targetPosition]);

  // Initialize Three.js on mount
  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    let threeScene: THREE.Scene | null = null;
    let threeRenderer: THREE.WebGLRenderer | null = null;
    threeScene = new THREE.Scene();
    threeRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    threeRenderer.setSize(500, 500); // Larger square renderer for bigger orb
    threeRenderer.setClearColor(0x000000, 0); // Transparent background
    mountRef.current.appendChild(threeRenderer.domElement);

    // Central orb (solid core)
    const coreGeometry = new THREE.SphereGeometry(1, 64, 64);
    const coreMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x4a90e2,
      emissive: 0x4a90e2,
      emissiveIntensity: 0.5,
      transmission: 0.9,
      thickness: 0.5,
      roughness: 0.1,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1
    });
    orbMesh = new THREE.Mesh(coreGeometry, coreMaterial);
    threeScene.add(orbMesh);

    // Volumetric glow layer (separate mesh for aura)
    const glowGeometry = new THREE.SphereGeometry(1.5, 32, 32);
    glowMaterial = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        intensity: { value: 1.0 },
        color: { value: new THREE.Color(0x4a90e2) }
      },
      vertexShader: `
        varying vec3 vNormal;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        uniform float intensity;
        uniform vec3 color;
        varying vec3 vNormal;

        void main() {
          float fresnel = 1.0 - dot(vNormal, vec3(0.0, 0.0, 1.0));
          float pulse = sin(time * 3.0) * 0.4 + 0.8; // Stronger pulse (3x speed, more variation)
          float alpha = fresnel * intensity * pulse * 1.5; // Increased intensity multiplier
          gl_FragColor = vec4(color, alpha);
        }
      `,
      transparent: true,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide
    });
    glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
    threeScene.add(glowMesh);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    threeScene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 1, 100);
    pointLight.position.set(0, 0, 5);
    threeScene.add(pointLight);

    // Camera
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    camera.position.z = 5;

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      if (orbMesh && glowMesh) {
        // Slow rotations for a calmer feel
        orbMesh.rotation.y += 0.0015;
        glowMesh.rotation.y -= 0.0009;
        if (glowMaterial) {
          glowMaterial.uniforms.time.value += 0.012;
        }
      }
      threeRenderer?.render(threeScene!, camera);
    };
    animate();

    return () => {
      mountRef.current?.removeChild(threeRenderer!.domElement);
      threeRenderer?.dispose();
      threeScene = null;
      threeRenderer = null;
      orbMesh = null;
      glowMesh = null;
      glowMaterial = null;
    };
  }, []);

  // Drag handlers (UI logic only)
  const onMouseDown = useCallback((e: React.MouseEvent) => {
    setIsDragging(true);
    dragOffset.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y
    };
    document.body.style.cursor = 'grabbing';
    // Pause attention while dragging
    onOrbHover(true);
  }, [position, onOrbHover]);

  const onMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging) return;
    setPosition({
      x: e.clientX - dragOffset.current.x,
      y: e.clientY - dragOffset.current.y
    });
  }, [isDragging]);

  const onMouseUp = useCallback(() => {
    setIsDragging(false);
    document.body.style.cursor = 'default';
    // Resume attention after drag
    setTimeout(() => onOrbHover(false), 1000);
  }, [onOrbHover]);

  useEffect(() => {
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, [onMouseMove, onMouseUp]);

  const handleClick = useCallback(() => {
    if (presence.visibility === 'latent') {
      // Record successful click interaction for learning
      const distance = Math.sqrt(
        Math.pow(position.x - lastCursorPosition.x, 2) +
        Math.pow(position.y - lastCursorPosition.y, 2)
      );

      orbLearningGraph.recordInteraction({
        cursorPosition: lastCursorPosition,
        orbPosition: position,
        distance,
        interaction: 'click',
        success: true
      });

      console.log('🧠 Learned from click interaction at distance:', distance.toFixed(1));

      // Start voice recognition
      if (recognition && !isListening) {
        try {
          recognition.start();
        } catch (error) {
          console.error('Failed to start voice recognition:', error);
        }
      }

      // Pause attention while escalating
      onOrbHover(true);
    }
  }, [presence.visibility, onOrbHover, position, recognition, isListening]);

  const size = presence.visibility === 'manifested' ? 600 : 200;
  const showDetails = presence.visibility !== 'latent' && size > 150;

  return (
    <Box
      position="fixed"
      left={`${position.x - size/2}px`}
      top={`${position.y - size/2}px`}
      width={`${size}px`}
      height={`${size}px`}
      zIndex={9999}
      pointerEvents="auto"
      onMouseDown={onMouseDown}
      onClick={handleClick}
      onMouseEnter={() => { if (allowHover) onOrbHover(true); }}
      onMouseLeave={() => { if (allowHover) onOrbHover(false); }}
    >
      {/* Three.js Canvas (true glow) */}
      <Box
        ref={mountRef}
        position="absolute"
        width="500px"
        height="500px"
        left="50%"
        top="50%"
        transform="translate(-50%, -50%)"
        pointerEvents="none" // Let events bubble to parent
      />

      {/* Animated Space Field (centered in orb) */}
      <Box
        position="absolute"
        left="50%"
        top="50%"
        transform="translate(-50%, -50%)"
        zIndex={6}
        pointerEvents="none"
        width="180px"
        height="180px"
      >
        <AnimatedSpaceField />
      </Box>

      {/* Space Field Controls removed from here; now embedded in orb center */}

      {/* Voice Control Button */}
      <Box
        position="absolute"
        top="-20px"
        right="-20px"
        width="40px"
        height="40px"
        borderRadius="full"
        bg={voiceEnabled ? "green.500" : "gray.500"}
        cursor="pointer"
        onClick={() => setVoiceEnabled(!voiceEnabled)}
        display="flex"
        alignItems="center"
        justifyContent="center"
        fontSize="16px"
        color="white"
        zIndex={12}
        boxShadow="0 2px 8px rgba(0,0,0,0.3)"
        _hover={{ transform: "scale(1.1)" }}
        transition="all 0.2s"
      >
        {voiceEnabled ? '🔊' : '🔇'}
      </Box>

      {/* Voice Listening Indicator */}
      {isListening && (
        <Box
          position="absolute"
          top="-20px"
          left="-20px"
          width="40px"
          height="40px"
          borderRadius="full"
          bg="red.500"
          animation="pulse 0.8s infinite"
          boxShadow="0 0 15px red"
          zIndex={11}
          display="flex"
          alignItems="center"
          justifyContent="center"
          fontSize="16px"
          color="white"
        >
          🎤
        </Box>
      )}

      {/* Speech Indicator */}
      {(presence as any).speech === 'listening' && (
        <Box
          position="absolute"
          bottom="-12px"
          right="-12px"
          width="30px"
          height="30px"
          borderRadius="full"
          bg="red.500"
          animation="pulse 1s infinite"
          boxShadow="0 0 10px red"
          zIndex={10}
        />
      )}

      {/* Resonance Display (manifested only) */}
      {showDetails && (
        <Box
          position="absolute"
          top="50%"
          left="50%"
          transform="translate(-50%, -50%)"
          fontSize="48px"
          fontWeight="bold"
          color="white"
          textShadow="0 0 30px rgba(0,0,0,0.8)"
          zIndex={5}
          pointerEvents="none"
        >
          {Math.round(presence.resonance * 100)}%
        </Box>
      )}

      {/* Confidence Display (manifested only) */}
      {showDetails && (
        <Box
          position="absolute"
          top="60%"
          left="50%"
          transform="translate(-50%, -50%)"
          fontSize="24px"
          fontWeight="bold"
          color="cyan"
          textShadow="0 0 20px rgba(0,0,0,0.8)"
          zIndex={5}
          pointerEvents="none"
        >
          Conf: {Math.round(confidence * 100)}%
        </Box>
      )}

    </Box>
  );
};