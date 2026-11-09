import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { CONTENT_KIND_LABELS, PLATFORM_LABELS, PRED_LABELS, hateTypeLabel } from "../../shared/labels.ts";
import { useFilters, toggleValue } from "../filters.tsx";
import { EMPTY_FILTERS, type Filters } from "../api.ts";

const SEARCH_DEBOUNCE_MS = 400;

/** Menu suspenso de filtro: fecha ao clicar fora ou com Esc. */
function Popover({
  label,
  count,
  children,
  onClear,
}: {
  label: string;
  count: number;
  children: ReactNode;
  onClear?: () => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div className="pop" ref={ref}>
      <button
        type="button"
        className={`pop-btn${count > 0 ? " on" : ""}${open ? " open" : ""}`}
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
      >
        <span>{label}</span>
        {count > 0 && <span className="pop-count">{count}</span>}
        <span className="pop-caret">▾</span>
      </button>
      {open && (
        <div className="pop-panel" role="group" aria-label={label}>
          {children}
          {onClear && count > 0 && (
            <button type="button" className="pop-clear" onClick={onClear}>
              limpar {label.toLowerCase()}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function OptionList({
  options,
  selected,
  onToggle,
}: {
  options: Array<{ value: string; label: string }>;
  selected: string[];
  onToggle: (value: string) => void;
}) {
  return (
    <div className="pop-list">
      {options.map((option) => (
        <label key={option.value} className="pop-option">
          <input type="checkbox" checked={selected.includes(option.value)} onChange={() => onToggle(option.value)} />
          <span>{option.label}</span>
        </label>
      ))}
    </div>
  );
}

export function FiltersBar() {
  const { filters, setFilters, meta, showPoliticalCharts, setShowPoliticalCharts } = useFilters();
  const update = (patch: Partial<Filters>) => setFilters({ ...filters, ...patch });

  const platformOptions = (meta?.platforms ?? []).map((p) => ({ value: p, label: PLATFORM_LABELS[p] ?? p }));
  const kindOptions = (meta?.contentKinds ?? []).map((k) => ({ value: k, label: CONTENT_KIND_LABELS[k] ?? k }));
  const predOptions = (meta?.predLabels ?? []).map((p) => ({ value: p, label: PRED_LABELS[p] ?? p }));
  const hateOptions = (meta?.hateTypes ?? []).map((code) => ({ value: code, label: hateTypeLabel(code) }));

  const activeCount =
    filters.platforms.length +
    filters.contentKinds.length +
    filters.predLabels.length +
    filters.hateTypes.length +
    (filters.dateStart || filters.dateEnd ? 1 : 0) +
    (filters.search ? 1 : 0);

  const activeChips = useMemo(() => {
    const chips: Array<{ key: string; label: string; clear: () => void }> = [];
    for (const value of filters.platforms) {
      chips.push({
        key: `p:${value}`,
        label: PLATFORM_LABELS[value] ?? value,
        clear: () => setFilters({ ...filters, platforms: filters.platforms.filter((v) => v !== value) }),
      });
    }
    for (const value of filters.contentKinds) {
      chips.push({
        key: `k:${value}`,
        label: CONTENT_KIND_LABELS[value] ?? value,
        clear: () => setFilters({ ...filters, contentKinds: filters.contentKinds.filter((v) => v !== value) }),
      });
    }
    for (const value of filters.predLabels) {
      chips.push({
        key: `l:${value}`,
        label: PRED_LABELS[value] ?? value,
        clear: () => setFilters({ ...filters, predLabels: filters.predLabels.filter((v) => v !== value) }),
      });
    }
    for (const value of filters.hateTypes) {
      chips.push({
        key: `h:${value}`,
        label: hateTypeLabel(value),
        clear: () => setFilters({ ...filters, hateTypes: filters.hateTypes.filter((v) => v !== value) }),
      });
    }
    if (filters.dateStart || filters.dateEnd) {
      chips.push({
        key: "date",
        label: `${filters.dateStart ?? "início"} → ${filters.dateEnd ?? meta?.maxDate ?? "hoje"}`,
        clear: () => setFilters({ ...filters, dateStart: undefined, dateEnd: undefined }),
      });
    }
    if (filters.search) {
      chips.push({
        key: "search",
        label: `“${filters.search}”`,
        clear: () => setFilters({ ...filters, search: undefined }),
      });
    }
    return chips;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, meta?.maxDate]);

  // Busca com debounce: sem isso cada tecla dispara um ILIKE sobre toda a base.
  const [draft, setDraft] = useState(filters.search ?? "");
  useEffect(() => {
    setDraft(filters.search ?? "");
  }, [filters.search]);
  useEffect(() => {
    if (draft === (filters.search ?? "")) return;
    const timer = setTimeout(() => update({ search: draft || undefined }), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [draft]);

  const setDateStart = (value: string) => {
    const next = value || undefined;
    const end = filters.dateEnd && next && next > filters.dateEnd ? next : filters.dateEnd;
    update({ dateStart: next, dateEnd: end });
  };
  const setDateEnd = (value: string) => {
    const next = value || undefined;
    const start = filters.dateStart && next && next < filters.dateStart ? next : filters.dateStart;
    update({ dateEnd: next, dateStart: start });
  };

  const maxDate = meta?.maxDate ?? null;
  const shiftDays = (days: number) => {
    if (!maxDate) return undefined;
    const date = new Date(`${maxDate}T00:00:00Z`);
    date.setUTCDate(date.getUTCDate() - (days - 1));
    return date.toISOString().slice(0, 10);
  };
  const presets: Array<{ label: string; apply: () => void; active: boolean }> = [
    {
      label: "Todo o período",
      apply: () => update({ dateStart: undefined, dateEnd: undefined }),
      active: !filters.dateStart && !filters.dateEnd,
    },
    { label: "Últimos 3 dias", apply: () => update({ dateStart: shiftDays(3), dateEnd: maxDate ?? undefined }), active: false },
    { label: "Últimos 7 dias", apply: () => update({ dateStart: shiftDays(7), dateEnd: maxDate ?? undefined }), active: false },
    {
      label: "Últimos 15 dias",
      apply: () => update({ dateStart: shiftDays(15), dateEnd: maxDate ?? undefined }),
      active: false,
    },
  ];

  const periodCount = filters.dateStart || filters.dateEnd ? 1 : 0;

  return (
    <section className="filters">
      <div className="filters-row">
        <div className="filters-search">
          <span className="filters-search-icon">⌕</span>
          <input
            type="search"
            placeholder="Buscar no texto dos conteúdos…"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            aria-label="Busca textual"
          />
          {draft && (
            <button type="button" className="filters-search-clear" onClick={() => setDraft("")} aria-label="Limpar busca">
              ×
            </button>
          )}
        </div>

        <div className="filters-pops">
          <Popover
            label="Plataforma"
            count={filters.platforms.length}
            onClear={() => setFilters({ ...filters, platforms: [] })}
          >
            <OptionList
              options={platformOptions}
              selected={filters.platforms}
              onToggle={(value) => setFilters(toggleValue(filters, "platforms", value))}
            />
          </Popover>

          <Popover
            label="Tipo"
            count={filters.contentKinds.length}
            onClear={() => setFilters({ ...filters, contentKinds: [] })}
          >
            <OptionList
              options={kindOptions}
              selected={filters.contentKinds}
              onToggle={(value) => setFilters(toggleValue(filters, "contentKinds", value))}
            />
          </Popover>

          <Popover
            label="Classificação"
            count={filters.predLabels.length}
            onClear={() => setFilters({ ...filters, predLabels: [] })}
          >
            <OptionList
              options={predOptions}
              selected={filters.predLabels}
              onToggle={(value) => setFilters(toggleValue(filters, "predLabels", value))}
            />
          </Popover>

          <Popover
            label="Tipos de preconceito"
            count={filters.hateTypes.length}
            onClear={() => setFilters({ ...filters, hateTypes: [] })}
          >
            <OptionList
              options={hateOptions}
              selected={filters.hateTypes}
              onToggle={(value) => setFilters(toggleValue(filters, "hateTypes", value))}
            />
          </Popover>

          <Popover
            label="Período"
            count={periodCount}
            onClear={() => setFilters({ ...filters, dateStart: undefined, dateEnd: undefined })}
          >
            <div className="pop-presets">
              {presets.map((preset) => (
                <button
                  key={preset.label}
                  type="button"
                  className={`pop-preset${preset.active ? " on" : ""}`}
                  onClick={preset.apply}
                >
                  {preset.label}
                </button>
              ))}
            </div>
            <div className="pop-dates">
              <label>
                De
                <input
                  type="date"
                  value={filters.dateStart ?? ""}
                  min={meta?.dashboardMinDate}
                  max={meta?.maxDate ?? undefined}
                  onChange={(event) => setDateStart(event.target.value)}
                />
              </label>
              <label>
                Até
                <input
                  type="date"
                  value={filters.dateEnd ?? ""}
                  min={meta?.dashboardMinDate}
                  max={meta?.maxDate ?? undefined}
                  onChange={(event) => setDateEnd(event.target.value)}
                />
              </label>
            </div>
          </Popover>

          <button
            type="button"
            className={`pop-btn${showPoliticalCharts ? " on" : ""}`}
            onClick={() => setShowPoliticalCharts(!showPoliticalCharts)}
            aria-pressed={showPoliticalCharts}
            aria-label={showPoliticalCharts ? "Ocultar ódio político nos gráficos" : "Exibir ódio político nos gráficos"}
            title={showPoliticalCharts ? "Ocultar ódio político nos gráficos" : "Exibir ódio político nos gráficos"}
          >
            <svg aria-hidden="true" viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" />
              <circle cx="12" cy="12" r="2.8" fill={showPoliticalCharts ? "currentColor" : "none"} />
            </svg>
            <span>{showPoliticalCharts ? "Ocultar ódio político" : "Exibir ódio político"}</span>
          </button>
        </div>
      </div>

      {activeChips.length > 0 && (
        <div className="filters-active-row">
          <span className="filters-active-label">
            {activeChips.length} {activeChips.length === 1 ? "filtro" : "filtros"}
          </span>
          {activeChips.map((chip) => (
            <button key={chip.key} type="button" className="chip chip-on" onClick={chip.clear} title="Remover filtro">
              {chip.label} <span className="chip-x">×</span>
            </button>
          ))}
          {activeCount > 0 && (
            <button type="button" className="filters-clear" onClick={() => setFilters({ ...EMPTY_FILTERS })}>
              Limpar tudo
            </button>
          )}
        </div>
      )}
    </section>
  );
}
