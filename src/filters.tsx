import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { useSearchParams } from "react-router-dom";
import type { Filters, Meta } from "./api.ts";

type Ctx = {
  filters: Filters;
  setFilters: (next: Filters) => void;
  meta: Meta | null;
  showPoliticalCharts: boolean;
  setShowPoliticalCharts: (show: boolean) => void;
};

const FiltersContext = createContext<Ctx | null>(null);

const KEYS: Array<keyof Filters> = [
  "platforms",
  "contentKinds",
  "predLabels",
  "hateTypes",
  "dateStart",
  "dateEnd",
  "search",
  "excludePolitical",
];

const ARRAY_KEYS: Array<keyof Filters> = ["platforms", "contentKinds", "predLabels", "hateTypes"];

function split(value: string | null): string[] {
  if (!value) return [];
  return value.split(",").map((v) => v.trim()).filter(Boolean);
}

export function FiltersProvider({ meta, children }: { meta: Meta | null; children: ReactNode }) {
  const [params, setParams] = useSearchParams();
  const [showPoliticalCharts, setShowPoliticalCharts] = useState(false);

  const filters = useMemo<Filters>(
    () => ({
      platforms: split(params.get("platforms")),
      contentKinds: split(params.get("contentKinds")),
      predLabels: split(params.get("predLabels")),
      hateTypes: split(params.get("hateTypes")),
      dateStart: params.get("dateStart") ?? undefined,
      dateEnd: params.get("dateEnd") ?? undefined,
      search: params.get("search") ?? undefined,
      // A exclusão de conteúdos políticos saiu da interface; o único controle
      // restante afeta apenas a visibilidade da categoria nos gráficos.
      excludePolitical: false,
    }),
    [params],
  );

  const value = useMemo<Ctx>(
    () => ({
      meta,
      filters,
      showPoliticalCharts,
      setShowPoliticalCharts,
      setFilters: (next: Filters) => {
        const updated = new URLSearchParams(params);
        for (const key of KEYS) {
          const raw = next[key];
          if (key === "excludePolitical") {
            if (raw) updated.set(key, "1");
            else updated.delete(key);
            continue;
          }
          if (Array.isArray(raw)) {
            if (raw.length) updated.set(key, raw.join(","));
            else updated.delete(key);
          } else if (raw) {
            updated.set(key, String(raw));
          } else {
            updated.delete(key);
          }
        }
        setParams(updated);
      },
    }),
    [filters, meta, params, setParams, showPoliticalCharts],
  );

  return <FiltersContext.Provider value={value}>{children}</FiltersContext.Provider>;
}

export function useFilters(): Ctx {
  const ctx = useContext(FiltersContext);
  if (!ctx) throw new Error("useFilters fora do FiltersProvider");
  return ctx;
}

/** Alterna um valor dentro de um filtro de lista. */
export function toggleValue(filters: Filters, key: (typeof ARRAY_KEYS)[number], value: string): Filters {
  const current = filters[key] as string[];
  const has = current.includes(value);
  return { ...filters, [key]: has ? current.filter((v) => v !== value) : [...current, value] };
}
