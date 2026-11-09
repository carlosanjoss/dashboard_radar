/** Camada de acesso à API do dashboard. */

export type Filters = {
  platforms: string[];
  contentKinds: string[];
  predLabels: string[];
  hateTypes: string[];
  dateStart?: string;
  dateEnd?: string;
  search?: string;
  /** Retira da analise os conteudos cujo unico tipo de odio e o politico. */
  excludePolitical?: boolean;
};

export const EMPTY_FILTERS: Filters = {
  platforms: [],
  contentKinds: [],
  predLabels: [],
  hateTypes: [],
};

export type Meta = {
  modelName: string;
  minDate: string | null;
  maxDate: string | null;
  windowRows: number;
  totalRows: number;
  platforms: string[];
  contentKinds: string[];
  predLabels: string[];
  hateTypes: string[];
  categoryHierarchy: string[];
  dashboardMinDate: string;
};

export type Row = Record<string, unknown>;

/** Serializa filtros + extras em query string (só o que está preenchido). */
export function toQuery(filters: Filters, extra: Record<string, unknown> = {}): string {
  const params = new URLSearchParams();
  if (filters.platforms.length) params.set("platforms", filters.platforms.join(","));
  if (filters.contentKinds.length) params.set("contentKinds", filters.contentKinds.join(","));
  if (filters.predLabels.length) params.set("predLabels", filters.predLabels.join(","));
  if (filters.hateTypes.length) params.set("hateTypes", filters.hateTypes.join(","));
  if (filters.dateStart) params.set("dateStart", filters.dateStart);
  if (filters.dateEnd) params.set("dateEnd", filters.dateEnd);
  if (filters.search) params.set("search", filters.search);
  if (filters.excludePolitical) params.set("excludePolitical", "1");
  for (const [key, value] of Object.entries(extra)) {
    if (value === undefined || value === null || value === "") continue;
    params.set(key, String(value));
  }
  return params.toString();
}

export async function api<T>(path: string, filters?: Filters, extra?: Record<string, unknown>): Promise<T> {
  const qs = filters ? toQuery(filters, extra) : "";
  const res = await fetch(qs ? `${path}?${qs}` : path);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`HTTP ${res.status}: ${body.slice(0, 200)}`);
  }
  const data = (await res.json()) as T & { error?: string };
  if (data && typeof data === "object" && "error" in data && data.error) {
    throw new Error(String(data.error));
  }
  return data as T;
}

/* ----------------------------------------------------------- formatação */

export function fmtInt(value: unknown): string {
  const n = Number(value ?? 0);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString("pt-BR");
}

export function fmtPct(value: unknown, digits = 2): string {
  const n = Number(value ?? 0);
  if (!Number.isFinite(n)) return "—";
  return `${n.toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits })}%`;
}

export function fmtProb(value: unknown, digits = 3): string {
  const n = Number(value ?? 0);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export function fmtDate(value: unknown): string {
  if (!value) return "—";
  const d = new Date(String(value));
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleDateString("pt-BR");
}

export function asNumber(value: unknown): number {
  const n = Number(value ?? 0);
  return Number.isFinite(n) ? n : 0;
}

/** Intervalo de confiança de Wilson (95%) para uma proporção — melhora a leitura de amostras pequenas. */
export function wilson(successes: number, total: number, z = 1.96): { low: number; high: number } {
  if (total <= 0) return { low: 0, high: 0 };
  const phat = successes / total;
  const denom = 1 + (z * z) / total;
  const center = (phat + (z * z) / (2 * total)) / denom;
  const margin = (z * Math.sqrt((phat * (1 - phat)) / total + (z * z) / (4 * total * total))) / denom;
  return { low: Math.max(0, (center - margin) * 100), high: Math.min(100, (center + margin) * 100) };
}