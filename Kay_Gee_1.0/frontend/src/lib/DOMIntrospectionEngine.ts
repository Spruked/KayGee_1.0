type Category = "action" | "input" | "navigation";

interface ElementPosition {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface SemanticElement {
  id: string;
  category: Category;
  priority: number;
  label: string;
  position: ElementPosition;
}

export interface SemanticMap {
  actions: SemanticElement[];
  inputs: SemanticElement[];
  navigation: SemanticElement[];
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function visible(el: Element): boolean {
  if (!(el instanceof HTMLElement)) return false;
  const style = window.getComputedStyle(el);
  if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) return false;
  const rect = el.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0;
}

function extractLabel(el: Element): string {
  const aria = el.getAttribute("aria-label");
  const title = el.getAttribute("title");
  const text = (el.textContent || "").trim();
  return aria || title || text || el.tagName.toLowerCase();
}

class DOMIntrospectionEngine {
  private cursor = { x: 0, y: 0 };

  updateCursorPosition(point: { x: number; y: number }): void {
    this.cursor = { x: point.x, y: point.y };
  }

  private scoreElement(rect: DOMRect, category: Category): number {
    const viewportArea = Math.max(window.innerWidth * window.innerHeight, 1);
    const areaRatio = clamp((rect.width * rect.height) / viewportArea, 0, 0.2);

    const dx = this.cursor.x - (rect.left + rect.width / 2);
    const dy = this.cursor.y - (rect.top + rect.height / 2);
    const distance = Math.sqrt(dx * dx + dy * dy);
    const distanceScore = 1 / (1 + distance / 300);

    const categoryWeight = category === "action" ? 1.0 : category === "input" ? 0.9 : 0.8;
    return clamp(categoryWeight * (0.55 * distanceScore + 0.45 * areaRatio * 8), 0.1, 1.0);
  }

  private mapElements(selector: string, category: Category): SemanticElement[] {
    const nodes = Array.from(document.querySelectorAll(selector));
    const result: SemanticElement[] = [];

    for (const node of nodes) {
      if (!visible(node)) continue;
      const rect = node.getBoundingClientRect();
      result.push({
        id: `${category}:${result.length}:${extractLabel(node).slice(0, 24)}`,
        category,
        priority: this.scoreElement(rect, category),
        label: extractLabel(node),
        position: {
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2,
          width: rect.width,
          height: rect.height,
        },
      });
    }

    return result.sort((a, b) => b.priority - a.priority).slice(0, 40);
  }

  scanPage(): SemanticMap {
    if (typeof window === "undefined" || typeof document === "undefined") {
      return { actions: [], inputs: [], navigation: [] };
    }

    return {
      actions: this.mapElements("button,[role='button'],[data-action],.btn,.button", "action"),
      inputs: this.mapElements("input,textarea,select,[contenteditable='true']", "input"),
      navigation: this.mapElements("a[href],nav a,[role='link']", "navigation"),
    };
  }
}

export const domIntrospection = new DOMIntrospectionEngine();
