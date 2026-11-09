import { useEffect, useLayoutEffect, useRef, useState } from "react";

export type CloudWord = { text: string; value: number };

type Placed = {
  text: string;
  value: number;
  x: number;
  y: number;
  fontSize: number;
  weight: number;
  tone: number;
};

const FONT_STACK = 'Inter, "Segoe UI", system-ui, -apple-system, sans-serif';
const TONES = 6;

/** Medidor de texto reaproveitado entre layouts. */
function makeMeasurer() {
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  return (text: string, fontSize: number, weight: number) => {
    if (!ctx) return text.length * fontSize * 0.58;
    ctx.font = `${weight} ${fontSize}px ${FONT_STACK}`;
    return ctx.measureText(text).width;
  };
}

function overlaps(
  a: { x: number; y: number; w: number; h: number },
  boxes: Array<{ x: number; y: number; w: number; h: number }>,
) {
  for (const b of boxes) {
    if (a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y) return true;
  }
  return false;
}

/**
 * Nuvem de palavras com posicionamento em espiral (Archimedean) e teste de
 * colisão: as palavras maiores entram primeiro e ocupam o centro; as menores
 * vão sendo acomodadas em volta. Determinística — não "pula" a cada render.
 */
export function WordCloud({ words, height = 420 }: { words: CloudWord[]; height?: number }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [width, setWidth] = useState(0);
  const [placed, setPlaced] = useState<Placed[]>([]);
  const [skipped, setSkipped] = useState(0);

  useLayoutEffect(() => {
    const element = containerRef.current;
    if (!element) return;
    const update = () => setWidth(element.clientWidth);
    update();
    const observer = new ResizeObserver(update);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!width || !words.length) {
      setPlaced([]);
      return;
    }

    const measure = makeMeasurer();
    const sorted = [...words].sort((a, b) => b.value - a.value);
    const max = sorted[0].value;
    const min = sorted[sorted.length - 1].value;
    const minFont = width < 520 ? 11 : 12.5;
    const maxFont = Math.max(24, Math.min(width < 520 ? 30 : 48, height / 9));

    const sizeFor = (value: number) => {
      if (max === min) return (minFont + maxFont) / 2;
      const t = (Math.sqrt(value) - Math.sqrt(min)) / (Math.sqrt(max) - Math.sqrt(min));
      return minFont + Math.max(0, Math.min(1, t)) * (maxFont - minFont);
    };

    const boxes: Array<{ x: number; y: number; w: number; h: number }> = [];
    const result: Placed[] = [];
    const centerX = width / 2;
    const centerY = height / 2;
    const padX = 7;
    const padY = 4;
    let skippedCount = 0;

    sorted.forEach((word, index) => {
      const fontSize = sizeFor(word.value);
      const weight = fontSize > maxFont * 0.72 ? 780 : fontSize > maxFont * 0.45 ? 660 : 560;
      const boxW = measure(word.text, fontSize, weight) + padX * 2;
      const boxH = fontSize * 1.16 + padY * 2;

      let placedBox: { x: number; y: number; w: number; h: number } | null = null;
      const angleStep = 0.19;
      for (let step = 0; step < 2600; step += 1) {
        const angle = step * angleStep;
        const radius = 2.6 * angle;
        const x = centerX + radius * Math.cos(angle) * 1.6 - boxW / 2;
        const y = centerY + radius * Math.sin(angle) * 0.95 - boxH / 2;
        if (x < 2 || y < 2 || x + boxW > width - 2 || y + boxH > height - 2) continue;
        const candidate = { x, y, w: boxW, h: boxH };
        if (!overlaps(candidate, boxes)) {
          placedBox = candidate;
          break;
        }
      }

      if (!placedBox) {
        skippedCount += 1;
        return;
      }

      boxes.push(placedBox);
      result.push({
        text: word.text,
        value: word.value,
        x: placedBox.x + padX,
        y: placedBox.y + padY,
        fontSize,
        weight,
        tone: index % TONES,
      });
    });

    setPlaced(result);
    setSkipped(skippedCount);
  }, [words, width, height]);

  return (
    <div>
      <div className="wordcloud" ref={containerRef} style={{ height }}>
        {placed.map((word) => (
          <span
            key={word.text}
            className={`wc-word wc-t${word.tone}`}
            style={{
              left: `${word.x}px`,
              top: `${word.y}px`,
              fontSize: `${word.fontSize}px`,
              fontWeight: word.weight,
            }}
            title={`${word.text} · ${word.value.toLocaleString("pt-BR")} ocorrências`}
          >
            {word.text}
          </span>
        ))}
        {!placed.length && <div className="empty">Sem termos para exibir.</div>}
      </div>
      {skipped > 0 && (
        <p className="card-sub" style={{ marginTop: 8 }}>
          {skipped} termo{skipped === 1 ? "" : "s"} não caberia{skipped === 1 ? "" : "m"} no espaço disponível e
          {skipped === 1 ? " ficou" : " ficaram"} fora da nuvem — amplie a janela ou reduza o número de termos.
        </p>
      )}
    </div>
  );
}