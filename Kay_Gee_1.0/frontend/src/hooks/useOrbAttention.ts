import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { orbLearningGraph } from '../lib/OrbLearningGraph';
import { domIntrospection } from '../lib/DOMIntrospectionEngine';
import { PresenceStore } from '../store/presenceStore';

/**
 * ATTENTION SYSTEM - Pure UI/UX Layer
 *
 * Tracks cursor position and user focus zones.
 * DOES NOT touch PresenceStore (epistemic state is sacred).
 * Smoothly animates Orb toward areas of interest.
 */
export function useOrbAttention(isEnabled: boolean = true) {
  const [targetPosition, setTargetPosition] = useState({ x: window.innerWidth - 120, y: window.innerHeight - 120 });
  const lastCursor = useRef({ x: 0, y: 0 });
  const lastOrbPosition = useRef({ x: window.innerWidth - 120, y: window.innerHeight - 120 });
  // Small cursor history for short-term prediction (anticipation)
  const lastPositionsRef = useRef<Array<{ x: number; y: number; t: number }>>([]);
  const interactionTimer = useRef<number | null>(null);
  const isOrbHoveredRef = useRef(false);

  // Get learned behavior with refs for performance
    const optimalDistanceRef = useRef(orbLearningGraph.getOptimalDistance());
    // Wire confidence with a safe fallback and clamp so it never becomes zero
    const _initialConf = (() => {
      try {
        const c = orbLearningGraph.getConfidence();
        const presence = PresenceStore.get ? PresenceStore.get() : null;
        const presRes = presence && typeof (presence as any).resonance === 'number' ? (presence as any).resonance : 0;
        return Math.max(0.15, c || presRes || 0.15);
      } catch {
        return 0.15;
      }
    })();
    const confidenceRef = useRef<number>(_initialConf);

  // Update learning refs when they change
  useEffect(() => {
    const unsubscribe = PresenceStore.subscribe(() => {
      optimalDistanceRef.current = orbLearningGraph.getOptimalDistance();
        try {
          const conf = orbLearningGraph.getConfidence();
          const pres = PresenceStore.get ? PresenceStore.get() : null;
          const presRes = pres && typeof (pres as any).resonance === 'number' ? (pres as any).resonance : 0;
          confidenceRef.current = Math.max(0.15, conf || presRes || 0.15);
        } catch (e) {
          // keep previous confidence if update fails
        }
    });
    return unsubscribe;
  }, []);

  // Cursor tracking (throttled)
  useEffect(() => {
    if (!isEnabled) return;

    const handleMouseMove = throttle((e: MouseEvent) => {
      const now = Date.now();
      lastCursor.current = { x: e.clientX, y: e.clientY };

      // Maintain a short history for velocity-based prediction
      const hist = lastPositionsRef.current;
      hist.push({ x: e.clientX, y: e.clientY, t: now });
      if (hist.length > 8) hist.shift();

      // Update DOM introspection engine with cursor position
      domIntrospection.updateCursorPosition({ x: e.clientX, y: e.clientY });
    }, 16);

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [isEnabled]);

  // Scan page for interactive elements
  const semanticMap = useMemo(() => {
    if (!isEnabled) return null;
    return domIntrospection.scanPage();
  }, [isEnabled]); // Re-scan when enabled/disabled

  // Find highest priority element near cursor
  const getTopAttentionElement = useCallback(() => {
    if (!semanticMap) return null;

    const allElements = [
      ...semanticMap.actions,
      ...semanticMap.inputs,
      ...semanticMap.navigation
    ];

    return allElements
      .filter(el => el.priority > 0.5) // Only high-priority elements
      .sort((a, b) => b.priority - a.priority)[0] || null;
  }, [semanticMap]);

  // Position maintenance with learning and semantic awareness
  useEffect(() => {
    if (!isEnabled) {
      setTargetPosition({ x: window.innerWidth - 120, y: window.innerHeight - 120 });
      return;
    }

    const animate = () => {
      const cursorPos = lastCursor.current;
      // Use the last known orb position for smoother continuity
      const currentPos = { ...lastOrbPosition.current };
      const topElement = getTopAttentionElement();

      // Check if cursor is over a button (special handling)
      const isOverButton = topElement &&
        topElement.category === 'action' &&
        topElement.priority > 0.8 &&
        Math.abs(cursorPos.x - topElement.position.x) < topElement.position.width / 2 &&
        Math.abs(cursorPos.y - topElement.position.y) < topElement.position.height / 2;

      // Update orb position tracking for learning (persist current)
      lastOrbPosition.current = currentPos;

      // Get learned optimal distance (or fallback)
      // Use a clamped confidence value so zero doesn't collapse behavior
      const effConfidence = Math.max(0.15, confidenceRef.current);
      const learnedDistance = effConfidence > 0.25
        ? optimalDistanceRef.current
        : 320; // larger default if not confident to keep orb further from cursor

      // Special handling for buttons - give more space
      const effectiveDistance = isOverButton ? learnedDistance * 2.2 : learnedDistance * 1.8;

      // Attempt short-term prediction of next click using cursor history
      const now = Date.now();
      const hist = lastPositionsRef.current;
      let predicted = { x: cursorPos.x, y: cursorPos.y };
      if (hist.length >= 2) {
        // Use the oldest sample within the buffered history for a stable estimate
        const earliest = hist[0];
        const dt = Math.max(1, now - earliest.t);
        const vx = (cursorPos.x - earliest.x) / dt; // px per ms
        const vy = (cursorPos.y - earliest.y) / dt; // px per ms

          // Smaller lookahead to avoid overshooting; use clamped confidence
          const lookaheadMs = 100 + Math.min(120, Math.round(effConfidence * 120));
        predicted = {
          x: cursorPos.x + vx * lookaheadMs,
          y: cursorPos.y + vy * lookaheadMs
        };
      }

      // Compute approach vector from cursor to predicted click
      const dxp = predicted.x - cursorPos.x;
      const dyp = predicted.y - cursorPos.y;
      const distp = Math.sqrt(dxp * dxp + dyp * dyp) || 0.0001;
      const unitDirX = dxp / distp;
      const unitDirY = dyp / distp;
      // Perpendicular vector to offset to the side (avoid blocking direct path)
      const perpX = -unitDirY;
      const perpY = unitDirX;

      // If we have meaningful motion, bias toward predicted click but stay out of the path
      let finalX: number;
      let finalY: number;

      if (distp > 2) {
        // Offset farther from the predicted click so the orb stays out of the way
        const offsetDistance = effectiveDistance * 0.9;
        const avoidanceOffset = learnedDistance * 0.6; // move further behind the click to avoid being in front

        finalX = predicted.x + perpX * offsetDistance - unitDirX * avoidanceOffset;
        finalY = predicted.y + perpY * offsetDistance - unitDirY * avoidanceOffset;

        // Blend slightly toward any high-priority element (conservative)
        if (topElement && topElement.priority > 0.7 && !isOverButton) {
          const elementBlend = Math.min(confidenceRef.current * 0.5, 0.35);
          finalX = finalX * (1 - elementBlend) + topElement.position.x * elementBlend;
          finalY = finalY * (1 - elementBlend) + (topElement.position.y - 80) * elementBlend;
        } else {
          // Blend toward preferred zones if present
          const zones = orbLearningGraph.getPreferredZonesNear({ x: finalX, y: finalY });
          if (zones.length > 0) {
            const strongest = zones[0];
            const blend = Math.min(confidenceRef.current, 0.4);
            finalX = finalX * (1 - blend) + strongest.x * blend;
            finalY = finalY * (1 - blend) + strongest.y * blend;
          }
        }

        // Enforce rule: never position in front of cursor along approach vector
        const relX = finalX - cursorPos.x;
        const relY = finalY - cursorPos.y;
        const forwardDot = relX * unitDirX + relY * unitDirY;
        if (forwardDot > -60) {
          // push it further behind the cursor path (stronger enforcement)
          finalX -= unitDirX * (forwardDot + 80);
          finalY -= unitDirY * (forwardDot + 80);
        }

        // Keep a minimum distance from cursor to avoid overlap and strictly prevent hovering
        const distFromCursor = Math.sqrt(relX * relX + relY * relY);
        // Ensure a relatively large minimum — never hover the cursor
        const minAllowed = Math.max(effectiveDistance * 0.8, 350);
        if (distFromCursor < minAllowed) {
          const pushFactor = (minAllowed - distFromCursor) + 25;
          finalX += (relX / (distFromCursor || 1)) * pushFactor;
          finalY += (relY / (distFromCursor || 1)) * pushFactor;
        }
      } else {
        // Fallback to previous cursor-following behavior when motion too small
        finalX = cursorPos.x + Math.cos(Math.atan2(cursorPos.y - currentPos.y, cursorPos.x - currentPos.x)) * effectiveDistance;
        finalY = cursorPos.y + Math.sin(Math.atan2(cursorPos.y - currentPos.y, cursorPos.x - currentPos.x)) * effectiveDistance;

        const zones = orbLearningGraph.getPreferredZonesNear({ x: finalX, y: finalY });
        if (zones.length > 0) {
          const strongest = zones[0];
          const blend = Math.min(confidenceRef.current, 0.4);
          finalX = finalX * (1 - blend) + strongest.x * blend;
          finalY = finalY * (1 - blend) + strongest.y * blend;
        }
      }

      // Smoothly move toward computed target — slower for calmer motion
      // Limit per-frame step to avoid popping when predictions change rapidly.
      const lerpAlpha = 0.004; // ultra-slow, extremely gentle movement
      const maxStep = 15; // tiny steps per frame for ultra-smooth motion
      setTargetPosition(prev => {
        const nx = prev.x + (finalX - prev.x) * lerpAlpha;
        const ny = prev.y + (finalY - prev.y) * lerpAlpha;
        const dx = nx - prev.x;
        const dy = ny - prev.y;
        const stepDist = Math.sqrt(dx * dx + dy * dy);
        if (stepDist > maxStep) {
          const scale = maxStep / stepDist;
          return { x: prev.x + dx * scale, y: prev.y + dy * scale };
        }
        return { x: nx, y: ny };
      });

      requestAnimationFrame(animate);
    };

    const raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [isEnabled, targetPosition, getTopAttentionElement]);

  // Interaction recording with semantic context
  const onOrbHover = useCallback((isHovered: boolean) => {
    isOrbHoveredRef.current = isHovered;

    const currentDistance = Math.sqrt(
      Math.pow(lastOrbPosition.current.x - lastCursor.current.x, 2) +
      Math.pow(lastOrbPosition.current.y - lastCursor.current.y, 2)
    );

    const topElement = getTopAttentionElement();

    orbLearningGraph.recordInteraction({
      cursorPosition: lastCursor.current,
      orbPosition: lastOrbPosition.current,
      distance: currentDistance,
      interaction: isHovered ? 'hover' : 'idle',
      success: isHovered, // Hover = successful interaction
      context: {  // Full semantic context
        nearbyElements: semanticMap,
        topAttentionElement: topElement,
        pageComplexity: semanticMap ? Object.values(semanticMap).flat().filter(item => typeof item !== 'number').length : 0
      }
    });

    console.log('🧠 Recorded interaction with semantic context. Confidence:', (orbLearningGraph.getConfidence() * 100).toFixed(1) + '%');

    if (interactionTimer.current) clearTimeout(interactionTimer.current);

    if (isHovered) {
      interactionTimer.current = setTimeout(() => {
        orbLearningGraph.recordInteraction({
          cursorPosition: lastCursor.current,
          orbPosition: lastOrbPosition.current,
          distance: currentDistance,
          interaction: 'idle',
          success: true, // Prolonged engagement
          context: {
            nearbyElements: semanticMap,
            topAttentionElement: topElement,
            pageComplexity: semanticMap ? Object.values(semanticMap).flat().filter(item => typeof item !== 'number').length : 0
          }
        });
      }, 2000);
    }
  }, [semanticMap, getTopAttentionElement]);

  return {
    targetPosition,
    onOrbHover,
    isTracking: isEnabled,
    learningSnapshot: orbLearningGraph.exportLearning(),
    semanticMap,
    getTopAttentionElement
  };
}

// Throttle utility
function throttle<T extends (...args: any[]) => void>(fn: T, limit: number): T {
  let inThrottle = false;
  return ((...args: any[]) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  }) as T;
}