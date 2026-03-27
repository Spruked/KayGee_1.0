type Point = { x: number; y: number };

type InteractionKind =
  | "hover"
  | "idle"
  | "drag"
  | "click"
  | "speak_start"
  | "speak_end"
  | string;

interface InteractionRecord {
  cursorPosition: Point;
  orbPosition: Point;
  distance: number;
  interaction: InteractionKind;
  success: boolean;
  context?: unknown;
  timestamp?: number;
}

interface LearnedZone {
  x: number;
  y: number;
  weight: number;
  count: number;
  lastUpdated: number;
}

interface LearningState {
  interactions: InteractionRecord[];
  zones: LearnedZone[];
  optimalDistance: number;
  confidence: number;
  summonedCount: number;
  pathCrossedCount: number;
  lastUpdated: number;
}

interface LearningStats {
  confidence: number;
  totalInteractions: number;
  learnedZones: number;
  averageDistance: number;
  summonedCount: number;
  pathCrossedCount: number;
  lastUpdated: string;
}

const STORAGE_KEY = "kaygee.orb.learning.v1";
const DEFAULT_DISTANCE = 280;
const MAX_INTERACTIONS = 1500;
const MAX_ZONES = 24;

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function distance(a: Point, b: Point): number {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

function nowIso(ts: number): string {
  try {
    return new Date(ts).toISOString();
  } catch {
    return "";
  }
}

class OrbLearningGraph {
  private state: LearningState;

  constructor() {
    this.state = this.loadState();
  }

  private loadState(): LearningState {
    if (typeof window === "undefined" || !window.localStorage) {
      return this.defaultState();
    }
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) return this.defaultState();
      const parsed = JSON.parse(raw) as Partial<LearningState>;
      return {
        interactions: Array.isArray(parsed.interactions) ? parsed.interactions.slice(-MAX_INTERACTIONS) : [],
        zones: Array.isArray(parsed.zones) ? parsed.zones.slice(0, MAX_ZONES) : [],
        optimalDistance: typeof parsed.optimalDistance === "number" ? parsed.optimalDistance : DEFAULT_DISTANCE,
        confidence: typeof parsed.confidence === "number" ? parsed.confidence : 0.2,
        summonedCount: typeof parsed.summonedCount === "number" ? parsed.summonedCount : 0,
        pathCrossedCount: typeof parsed.pathCrossedCount === "number" ? parsed.pathCrossedCount : 0,
        lastUpdated: typeof parsed.lastUpdated === "number" ? parsed.lastUpdated : Date.now(),
      };
    } catch {
      return this.defaultState();
    }
  }

  private defaultState(): LearningState {
    return {
      interactions: [],
      zones: [],
      optimalDistance: DEFAULT_DISTANCE,
      confidence: 0.2,
      summonedCount: 0,
      pathCrossedCount: 0,
      lastUpdated: Date.now(),
    };
  }

  private persist(): void {
    if (typeof window === "undefined" || !window.localStorage) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
    } catch {
      // Ignore storage quota/transient failures.
    }
  }

  private updateZones(record: InteractionRecord): void {
    if (!record.success) return;
    const pos = record.orbPosition;
    const zoneRadius = 120;
    const existing = this.state.zones.find((zone) => distance(zone, pos) <= zoneRadius);

    if (existing) {
      const nextCount = existing.count + 1;
      existing.x = (existing.x * existing.count + pos.x) / nextCount;
      existing.y = (existing.y * existing.count + pos.y) / nextCount;
      existing.count = nextCount;
      existing.weight = clamp(existing.weight + 0.06, 0, 5);
      existing.lastUpdated = Date.now();
    } else {
      this.state.zones.push({
        x: pos.x,
        y: pos.y,
        weight: 1,
        count: 1,
        lastUpdated: Date.now(),
      });
    }

    this.state.zones.sort((a, b) => b.weight - a.weight || b.count - a.count);
    if (this.state.zones.length > MAX_ZONES) {
      this.state.zones = this.state.zones.slice(0, MAX_ZONES);
    }
  }

  recordInteraction(record: InteractionRecord): void {
    const enriched: InteractionRecord = {
      ...record,
      timestamp: record.timestamp ?? Date.now(),
    };

    this.state.interactions.push(enriched);
    if (this.state.interactions.length > MAX_INTERACTIONS) {
      this.state.interactions = this.state.interactions.slice(-MAX_INTERACTIONS);
    }

    if (record.interaction === "click") this.state.summonedCount += 1;
    if (record.distance < 60) this.state.pathCrossedCount += 1;

    this.updateZones(enriched);

    const sampled = this.state.interactions.slice(-120);
    const successful = sampled.filter((i) => i.success);
    const avgDistance =
      successful.length > 0
        ? successful.reduce((sum, i) => sum + (Number.isFinite(i.distance) ? i.distance : 0), 0) / successful.length
        : this.state.optimalDistance;

    // Smooth with EMA so the orb adapts without jitter.
    this.state.optimalDistance = clamp(this.state.optimalDistance * 0.84 + avgDistance * 0.16, 120, 520);

    const confidenceBase = clamp(sampled.length / 300, 0, 1);
    const successRate = sampled.length > 0 ? successful.length / sampled.length : 0;
    this.state.confidence = clamp(0.25 * confidenceBase + 0.75 * successRate, 0.1, 1.0);

    this.state.lastUpdated = Date.now();
    this.persist();
  }

  getOptimalDistance(): number {
    return clamp(this.state.optimalDistance, 120, 520);
  }

  getConfidence(): number {
    return clamp(this.state.confidence, 0.1, 1.0);
  }

  getPreferredZonesNear(point: Point): Array<{ x: number; y: number; weight: number; count: number }> {
    const ranked = this.state.zones
      .map((zone) => {
        const d = distance(zone, point);
        const locality = 1 / (1 + d / 200);
        const score = zone.weight * locality;
        return { ...zone, score };
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);

    return ranked.map((z) => ({ x: z.x, y: z.y, weight: z.weight, count: z.count }));
  }

  getStats(): LearningStats {
    const distances = this.state.interactions.map((i) => i.distance).filter((v) => Number.isFinite(v));
    const averageDistance =
      distances.length > 0 ? distances.reduce((sum, v) => sum + v, 0) / distances.length : this.state.optimalDistance;

    return {
      confidence: this.getConfidence(),
      totalInteractions: this.state.interactions.length,
      learnedZones: this.state.zones.length,
      averageDistance,
      summonedCount: this.state.summonedCount,
      pathCrossedCount: this.state.pathCrossedCount,
      lastUpdated: nowIso(this.state.lastUpdated),
    };
  }

  exportLearning(): LearningState {
    return JSON.parse(JSON.stringify(this.state)) as LearningState;
  }

  reset(): void {
    this.state = this.defaultState();
    this.persist();
  }
}

export const orbLearningGraph = new OrbLearningGraph();
