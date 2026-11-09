import { useEffect, useState } from "react";

const POLL_MS = 60_000;
const BUNDLE_RE = /assets\/index-[A-Za-z0-9_-]+\.js/;

/** Nome do bundle que ESTA página carregou (lido do <script type="module"> do index.html). */
function loadedBundle(): string | null {
  const el = Array.from(document.querySelectorAll<HTMLScriptElement>("script[src]")).find((s) =>
    s.src.includes("/assets/index-"),
  );
  return el ? (el.src.match(BUNDLE_RE)?.[0] ?? null) : null;
}

/**
 * O painel em produção é uma SPA: quando o `dist/` é republicado, a aba já aberta
 * continua rodando o bundle antigo — o servidor não empurra nada. Isso compara o
 * bundle carregado com o do index.html atual e oferece o recarregamento, em vez de
 * deixar a pessoa olhando uma versão velha sem saber.
 */
export function UpdateBanner() {
  const [stale, setStale] = useState(false);

  useEffect(() => {
    const current = loadedBundle();
    if (!current) return;
    let cancelled = false;

    const check = async () => {
      try {
        const res = await fetch(`/?_=${Date.now()}`, { cache: "no-store" });
        const html = await res.text();
        const next = html.match(BUNDLE_RE)?.[0] ?? null;
        if (!cancelled && next && next !== current) setStale(true);
      } catch {
        /* servidor reiniciando ou offline: silencioso de propósito */
      }
    };

    const id = window.setInterval(() => void check(), POLL_MS);
    const onWake = () => void check();
    window.addEventListener("focus", onWake);
    document.addEventListener("visibilitychange", onWake);
    void check();

    return () => {
      cancelled = true;
      window.clearInterval(id);
      window.removeEventListener("focus", onWake);
      document.removeEventListener("visibilitychange", onWake);
    };
  }, []);

  if (!stale) return null;

  return (
    <div className="update-banner" role="status">
      <span className="update-dot" aria-hidden="true" />
      <span>Nova versão do painel disponível.</span>
      <button type="button" onClick={() => window.location.reload()}>
        Recarregar
      </button>
    </div>
  );
}
