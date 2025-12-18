/**
 * 3D Space Field Component - Live Harmonic Geometry
 * 
 * Implements complex phasor calculation from JS visualizer:
 * center + magnitude * e^(i*phase)
 * 
 * Golden-ratio phase damping (π/sides * 0.618) creates emergent rotation
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface SpaceField3DProps {
  sides?: number;
  levels?: number;
  radius?: number;
  emergent?: boolean;
  rotationSpeed?: number;
}

interface Vertex3D {
  x: number;
  y: number;
  z: number;
}

export function SpaceField3D({
  sides = 6,
  levels = 3,
  radius = 2,
  emergent = true,
  rotationSpeed = 0.01
}: SpaceField3DProps) {
  const groupRef = useRef<THREE.Group>(null);
  const globalAngle = useRef(0);

  // Calculate multiplier (geometric series)
  const multiplier = (level: number, sides: number): number => {
    if (sides % 2 === 0) {
      return Math.pow(2, level - 2);
    } else {
      return Math.pow(1.5, level - 2);
    }
  };

  // Generate regular polygon vertices
  const generateVertices = (center: Vertex3D, radius: number, sides: number): Vertex3D[] => {
    const vertices: Vertex3D[] = [];
    const angleStep = (2 * Math.PI) / sides;

    for (let i = 0; i < sides; i++) {
      let angle: number;
      
      if (sides % 2 === 0) {
        // Even sides: vertex at top
        angle = angleStep * i;
      } else {
        // Odd sides: edge midpoint offset for symmetry
        angle = angleStep * i - (angleStep / 2);
      }

      const x = center.x + radius * Math.sin(angle);
      const y = center.y + radius * Math.cos(angle);
      
      vertices.push({ x, y, z: center.z });
    }

    return vertices;
  };

  // THE ROSETTA STONE: Complex phasor symmetry point calculation
  const calculateSymmetryPointPhasor = (
    center: Vertex3D,
    radius: number,
    sides: number,
    level: number,
    emergent: boolean
  ): Vertex3D => {
    if (level <= 1) return center;

    // Accumulate harmonic magnitude (geometric series)
    let totalMagnitude = 0;
    for (let l = 2; l <= level; l++) {
      const mult = multiplier(l, sides);
      totalMagnitude += radius * mult;
    }

    // Golden-ratio phase damping (Euler's formula: magnitude * e^(i*phase))
    const phase = emergent ? (Math.PI / sides) * 0.618 : 0;
    
    const offsetX = totalMagnitude * Math.cos(phase);
    const offsetY = totalMagnitude * Math.sin(phase);

    return {
      x: center.x + offsetX,
      y: center.y + offsetY,
      z: center.z
    };
  };

  // Rotate point around origin
  const rotatePoint = (point: Vertex3D, center: Vertex3D, angleDeg: number): Vertex3D => {
    const angleRad = (angleDeg * Math.PI) / 180;
    const cos = Math.cos(angleRad);
    const sin = Math.sin(angleRad);
    
    const dx = point.x - center.x;
    const dy = point.y - center.y;
    
    return {
      x: center.x + dx * cos - dy * sin,
      y: center.y + dx * sin + dy * cos,
      z: point.z
    };
  };

  // Generate space field geometry
  const geometry = useMemo(() => {
    const faces: Vertex3D[][] = [];
    const center: Vertex3D = { x: 0, y: 0, z: 0 };

    // Level 0: Base polygon
    const baseVertices = generateVertices(center, radius, sides);
    faces.push(baseVertices);

    // Level 1: Rotated copies around center
    const angleStep = 360 / sides;
    for (let i = 0; i < sides; i++) {
      const angle = angleStep * i;
      const rotatedVerts = baseVertices.map(v => rotatePoint(v, center, angle));
      faces.push(rotatedVerts);
    }

    // Levels 2+: Recursive expansion with phasor calculation
    let currentOrigin = center;
    for (let level = 2; level <= levels; level++) {
      // Calculate new origin using complex phasor
      currentOrigin = calculateSymmetryPointPhasor(currentOrigin, radius, sides, level, emergent);

      // Create rotated copies around new origin
      for (let i = 0; i < sides; i++) {
        const angle = angleStep * i;
        
        // Rotate all existing faces around new origin
        const previousLevelStart = faces.length - Math.pow(sides, level - 1);
        for (let j = previousLevelStart; j < faces.length; j++) {
          const rotatedVerts = faces[j].map(v => rotatePoint(v, currentOrigin, angle));
          faces.push(rotatedVerts);
        }
      }
    }

    return faces;
  }, [sides, levels, radius, emergent]);

  // Animation loop (PLL phase-locked rotation)
  useFrame((state, delta) => {
    if (groupRef.current) {
      // Update global angle with damping
      const damping = emergent ? 0.3 : 1.0;
      globalAngle.current += rotationSpeed * damping;
      
      // Apply rotation to entire field
      groupRef.current.rotation.z = globalAngle.current;
      
      // Slow rotation on other axes for depth
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.2) * 0.1;
      groupRef.current.rotation.y = Math.cos(state.clock.elapsedTime * 0.15) * 0.1;
    }
  });

  return (
    <group ref={groupRef}>
      {geometry.map((face, faceIdx) => {
        // Create line loop for each polygon
        const points = face.map(v => new THREE.Vector3(v.x, v.y, v.z));
        points.push(points[0]); // Close the loop

        // Color based on level (gradient from blue to cyan)
        const level = Math.floor(Math.log(faceIdx + 1) / Math.log(sides));
        const hue = 0.5 + level * 0.1; // Blue to cyan spectrum
        const color = new THREE.Color().setHSL(hue, 0.8, 0.6);

        return (
          <line key={faceIdx}>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={points.length}
                array={new Float32Array(points.flatMap(p => [p.x, p.y, p.z]))}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial color={color} linewidth={1} transparent opacity={0.6} />
          </line>
        );
      })}

      {/* Add subtle glow effect */}
      <pointLight position={[0, 0, 0]} intensity={0.5} color="#4fd1c5" distance={10} />
    </group>
  );
}

export default SpaceField3D;
