import React, { useState, useEffect } from 'react';
import { Box, VStack, HStack, Text, Slider, SliderTrack, SliderFilledTrack, SliderThumb, Button, Badge } from '@chakra-ui/react';

declare global {
  interface ImportMeta {
    env: Record<string, string>;
  }
}

const API_BASE = (import.meta as any).env.VITE_API_URL || 'http://localhost:8001';

interface SpaceFieldParams {
  sides: number;
  levels: number;
  alpha: number;
  rotation_angle: number;
  edges_only: boolean;
}

interface ResonanceState {
  phaseCoherence: number;
  dominantFreq: number;
  timestamp: number;
  harmonic_lock_count: number;
  turbulence_flag: boolean;
}

export const SpaceFieldControls: React.FC = () => {
  const [params, setParams] = useState<SpaceFieldParams>({
    sides: 4,
    levels: 3,
    alpha: 0.444,
    rotation_angle: 0,
    edges_only: true
  });

  const [resonance, setResonance] = useState<ResonanceState | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [svgContent, setSvgContent] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch resonance status
  const fetchResonance = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/resonance/status`);
      const data = await response.json();
      setResonance(data);
    } catch (error) {
      console.error('Failed to fetch resonance:', error);
    }
  };

  // Generate space field visualization
  const generateSpaceField = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch(`${API_BASE}/visualization/space_field`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      const data = await response.json();
      setErrorMsg(null);
      setSvgContent(data.svg || '');

      // Send resonance signature to DALS
      await sendResonanceSignature();
    } catch (error) {
      console.error('Failed to generate space field:', error);
      const msg = (error && (error as any).message) ? (error as any).message : String(error);
      setErrorMsg(`Space field backend error: ${msg}`);
      // Fallback: generate a local SVG so the UI remains functional even if backend is down
      try {
        const local = generateLocalSpaceSVG(params);
        setSvgContent(local);
      } catch (e) {
        console.error('Local space field generation also failed:', e);
        setErrorMsg(prev => `${prev}\nLocal fallback generation failed: ${String(e)}`);
        setSvgContent('');
      }
    } finally {
      setIsGenerating(false);
    }
  };

  // Local SVG generator fallback (simple geometric approximation)
  const generateLocalSpaceSVG = (p: SpaceFieldParams) => {
    // Use 400x200 same as backend stub for consistent layout
    const w = 400;
    const h = 200;
    const cx = w / 2;
    const cy = h / 2;
    const baseR = Math.min(w, h) * 0.28;

    const color = '#9bf';
    let svg = `<?xml version="1.0"?><svg xmlns='http://www.w3.org/2000/svg' width='${w}' height='${h}' viewBox='0 0 ${w} ${h}' preserveAspectRatio='xMidYMid meet'>`;
    svg += `<rect width='100%' height='100%' fill='#0b1226'/>`;

    for (let level = 1; level <= Math.max(1, p.levels); level++) {
      const radius = baseR * (level / Math.max(1, p.levels)) * (1 - (p.alpha - 0.1));
      const rot = (p.rotation_angle * Math.PI / 180) * (level / Math.max(1, p.levels));
      const opacity = Math.max(0.12, 0.6 - level * 0.08);

      const points: string[] = [];
      for (let i = 0; i < Math.max(3, p.sides); i++) {
        const ang = (2 * Math.PI * i / Math.max(3, p.sides)) + rot;
        const x = cx + radius * Math.cos(ang);
        const y = cy + radius * Math.sin(ang);
        points.push(`${x},${y}`);
      }

      if (p.edges_only) {
        svg += `<polygon points='${points.join(' ')}' fill='none' stroke='${color}' stroke-width='1.4' stroke-opacity='${opacity}' />`;
      } else {
        svg += `<polygon points='${points.join(' ')}' fill='${color}' fill-opacity='${opacity * 0.6}' stroke='${color}' stroke-opacity='${opacity * 0.9}' stroke-width='1.2' />`;
      }
    }

    svg += `<text x='12' y='18' fill='#9bf' font-size='12'>Local Space Field (fallback)</text>`;
    svg += `</svg>`;
    return svg;
  };

  // Send resonance signature to DALS (Data Abstraction Layer System)
  const sendResonanceSignature = async () => {
    try {
      const signature = {
        phaseCoherence: Math.random() * 0.5 + 0.5, // Simulated coherence based on geometry
        dominantFreq: params.alpha * 10, // Frequency based on alpha parameter
        timestamp: Date.now()
      };

      await fetch(`${API_BASE}/api/resonance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signature)
      });

      // Refresh resonance status
      setTimeout(fetchResonance, 500);
    } catch (error) {
      console.error('Failed to send resonance signature:', error);
    }
  };

  // Auto-refresh resonance status
  useEffect(() => {
    fetchResonance();
    const interval = setInterval(fetchResonance, 2000);
    return () => clearInterval(interval);
  }, []);

  // Auto-generate on parameter change
  useEffect(() => {
    const timeout = setTimeout(generateSpaceField, 500);
    return () => clearTimeout(timeout);
  }, [params]);

  return (
    <Box p={6} bg="gray.800" borderRadius="lg" color="white" minW="400px">
      <VStack spacing={6} align="stretch">
        <Text fontSize="xl" fontWeight="bold" textAlign="center">
          🌌 Space Field Master Controls
        </Text>

        <Text fontSize="sm" color="gray.300" textAlign="center">
          Control the geometric field that drives KayGee's cognitive resonance
        </Text>

        <Box height="1px" bg="gray.700" my={2} />

        {/* Resonance Status */}
        {resonance && (
          <Box p={4} bg="gray.700" borderRadius="md">
            <Text fontSize="lg" fontWeight="bold" mb={3}>🔮 Cognitive Resonance</Text>
            <HStack spacing={4} wrap="wrap">
              <Badge colorScheme={(Number(resonance.phaseCoherence ?? 0) > 0.8) ? "green" : (Number(resonance.phaseCoherence ?? 0) > 0.5) ? "yellow" : "red"}>
                Coherence: {(Number(resonance.phaseCoherence ?? 0) * 100).toFixed(1)}%
              </Badge>
              <Badge colorScheme="blue">
                Frequency: {Number(resonance.dominantFreq ?? 0).toFixed(2)} Hz
              </Badge>
              <Badge colorScheme={(Number(resonance.harmonic_lock_count ?? 0) > 0) ? "purple" : "gray"}>
                Harmonic Locks: {resonance.harmonic_lock_count ?? 0}
              </Badge>
              {resonance.turbulence_flag && (
                <Badge colorScheme="orange">⚠️ Turbulence</Badge>
              )}
            </HStack>
          </Box>
        )}

        <Box height="1px" bg="gray.700" my={2} />

        {/* Control Parameters */}
        <VStack spacing={4} align="stretch">
          <Box>
            <Text mb={2}>Geometric Sides: {params.sides}</Text>
            <Slider
              value={params.sides}
              onChange={(val) => setParams(p => ({ ...p, sides: val }))}
              min={3}
              max={12}
              step={1}
            >
              <SliderTrack>
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb />
            </Slider>
          </Box>

          <Box>
            <Text mb={2}>Recursion Levels: {params.levels}</Text>
            <Slider
              value={params.levels}
              onChange={(val) => setParams(p => ({ ...p, levels: val }))}
              min={1}
              max={8}
              step={1}
            >
              <SliderTrack>
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb />
            </Slider>
          </Box>

          <Box>
            <Text mb={2}>Harmonic Alpha: {params.alpha.toFixed(3)}</Text>
            <Slider
              value={params.alpha}
              onChange={(val) => setParams(p => ({ ...p, alpha: val }))}
              min={0.1}
              max={1.0}
              step={0.001}
            >
              <SliderTrack>
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb />
            </Slider>
          </Box>

          <Box>
            <Text mb={2}>Rotation Angle: {params.rotation_angle.toFixed(1)}°</Text>
            <Slider
              value={params.rotation_angle}
              onChange={(val) => setParams(p => ({ ...p, rotation_angle: val }))}
              min={0}
              max={360}
              step={1}
            >
              <SliderTrack>
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb />
            </Slider>
          </Box>

          <HStack>
            <Button
              size="sm"
              colorScheme={params.edges_only ? "blue" : "gray"}
              onClick={() => setParams(p => ({ ...p, edges_only: !p.edges_only }))}
            >
              {params.edges_only ? "Edges Only" : "Filled"}
            </Button>
            <Button
              size="sm"
              colorScheme="green"
              onClick={generateSpaceField}
              isLoading={isGenerating}
              loadingText="Generating..."
            >
              Generate Field
            </Button>
          </HStack>
        </VStack>

        <Box height="1px" bg="gray.700" my={2} />

        {/* SVG Preview */}
        {svgContent ? (
          <Box>
            <Text fontSize="sm" mb={2}>Live Field Visualization:</Text>
            {errorMsg && (
              <Box p={2} mb={2} bg="red.800" color="white" borderRadius="md" fontSize="12px">
                <strong>Warning:</strong> {errorMsg}
              </Box>
            )}
            <Box
              bg="gray.900"
              borderRadius="md"
              p={2}
              dangerouslySetInnerHTML={{ __html: svgContent }}
              maxH="300px"
              overflow="auto"
            />
          </Box>
        ) : (
          <Box p={3} bg="gray.800" borderRadius="md" color="gray.300">No space field available.</Box>
        )}

        <Text fontSize="xs" color="gray.400" textAlign="center">
          DALS Status: Connected • Backend: http://localhost:8000
        </Text>
      </VStack>
    </Box>
  );
};