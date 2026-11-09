import { useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import { EMPTY_FILTERS } from "./api.ts";
import { FiltersBar } from "./components/FiltersBar.tsx";
import { UpdateBanner } from "./components/UpdateBanner.tsx";
import { useApi, Status } from "./components/ui.tsx";
import { FiltersProvider } from "./filters.tsx";
import type { Meta } from "./api.ts";
import { Overview } from "./pages/Overview.tsx";
import { Platforms } from "./pages/Platforms.tsx";
import { Categories } from "./pages/Categories.tsx";
import { Temporal } from "./pages/Temporal.tsx";
import { Intersectionality } from "./pages/Intersectionality.tsx";
import { Terms } from "./pages/Terms.tsx";
import { Comments } from "./pages/Comments.tsx";

/** Navegação principal — barra horizontal no topo. */
const NAV = [
  { to: "/", label: "Panorama", icon: "◎", end: true },
  { to: "/plataformas", label: "Plataformas", icon: "▤" },
  { to: "/categorias", label: "Categorias", icon: "◈" },
  { to: "/temporal", label: "Temporal", icon: "◔" },
  { to: "/interseccionalidade", label: "Sobreposição", icon: "⊕" },
  { to: "/termos", label: "Termos", icon: "✸" },
  { to: "/comentarios", label: "Comentários", icon: "☰" },
];

/** Tema claro/escuro persistido em localStorage e aplicado via data-theme. */
function useTheme() {
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const saved = window.localStorage.getItem("radar-theme");
    if (saved === "light" || saved === "dark") return saved;
    return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("radar-theme", theme);
  }, [theme]);

  return { theme, toggle: () => setTheme((current) => (current === "dark" ? "light" : "dark")) };
}

function Topbar({ meta, theme, onToggleTheme }: { meta: Meta | null; theme: "light" | "dark"; onToggleTheme: () => void }) {
  return (
    <header className="topbar">
      <div className="topbar-row">
        <div className="brand">
          <span className="brand-title">RADAR</span>
        </div>
        <div className="topbar-meta">
          {meta ? (
            <>
              <span>
                <b>{Number(meta.windowRows).toLocaleString("pt-BR")}</b> conteúdos classificados
              </span>
              <span>
                janela {meta.minDate ?? "—"} → {meta.maxDate ?? "—"}
              </span>
            </>
          ) : (
            <span>conectando ao banco…</span>
          )}
        </div>
        <div className="topbar-actions">
          <button
            type="button"
            className="theme-toggle"
            onClick={onToggleTheme}
            title={theme === "dark" ? "Usar tema claro" : "Usar tema escuro"}
            aria-label="Alternar tema"
          >
            {theme === "dark" ? "☀" : "☾"}
          </button>
        </div>
      </div>

      <nav className="topnav" aria-label="Seções do painel">
        <div className="topnav-inner">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </header>
  );
}

export function App() {
  const meta = useApi<Meta>("/api/meta", EMPTY_FILTERS);
  const { theme, toggle: toggleTheme } = useTheme();

  if (meta.error) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Não foi possível conectar ao banco</h2>
        <Status loading={false} error={meta.error} />
      </div>
    );
  }

  return (
    <FiltersProvider meta={meta.data}>
      <div className="app">
        <Topbar meta={meta.data} theme={theme} onToggleTheme={toggleTheme} />
        <UpdateBanner />
        <div className="main">
          <div className="content">
            <FiltersBar />
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/plataformas" element={<Platforms />} />
              <Route path="/categorias" element={<Categories />} />
              <Route path="/temporal" element={<Temporal />} />
              <Route path="/interseccionalidade" element={<Intersectionality />} />
              <Route path="/termos" element={<Terms />} />
              <Route path="/comentarios" element={<Comments />} />
            </Routes>
          </div>
        </div>
      </div>
    </FiltersProvider>
  );
}
