/** Rótulos e hierarquia compartilhados entre servidor e cliente. */

export const HATE_TYPE_LABELS: Record<string, string> = {
  ageism: "Etarismo",
  aporophobia: "Classismo",
  body_shame: "Gordofobia",
  capacitism: "Capacitismo",
  lgbtphobia: "LGBTfobia",
  misogyny: "Sexismo",
  sexism: "Sexismo",
  other: "Outros",
  political: "Ódio político",
  racism: "Racismo",
  religious_intolerance: "Intolerância religiosa",
  xenophobia: "Xenofobia",
};

/**
 * Ordem canônica das categorias (sort_order de gemma_hate_categories).
 * Usada para montar as probabilidades "pegando as hierarquias".
 */
export const CATEGORY_HIERARCHY: string[] = [
  "ageism",
  "aporophobia",
  "body_shame",
  "capacitism",
  "lgbtphobia",
  "political",
  "racism",
  "religious_intolerance",
  "sexism",
  "xenophobia",
];

export const PLATFORM_LABELS: Record<string, string> = {
  facebook: "Facebook",
  instagram: "Instagram",
  reddit: "Reddit",
  telegram: "Telegram",
  tiktok: "TikTok",
  twitter: "Twitter",
  whatsapp: "WhatsApp",
  youtube: "YouTube",
};

/** Cores fixas por plataforma, compartilhadas por todos os gráficos. */
export const PLATFORM_COLORS: Record<string, string> = {
  facebook: "#1877f2",
  instagram: "#c13584",
  reddit: "#ff4500",
  telegram: "#229ed9",
  // O preto da marca desaparece no tema escuro; o rosa mantém contraste nos
  // dois temas e continua identificando o TikTok de forma consistente.
  tiktok: "#fe2c55",
  twitter: "#1d9bf0",
  whatsapp: "#25d366",
  youtube: "#ff0000",
};

/** Ódio político fica disponível apenas nas visualizações de interseccionalidade. */
export const CHART_EXCLUDED_HATE_TYPES = new Set(["political"]);

export const CONTENT_KIND_LABELS: Record<string, string> = {
  post: "Post",
  comment: "Comentário",
};

export const PRED_LABELS: Record<string, string> = {
  hate: "Discurso de ódio",
  nao_hate: "Sem discurso de ódio",
};

export const MESSAGING_PLATFORMS = new Set(["telegram", "whatsapp"]);

export const EXCLUDED_HATE_TYPES = new Set(["other"]);

export function hateTypeLabel(code: string | null | undefined): string {
  if (!code) return "—";
  return HATE_TYPE_LABELS[code] ?? code;
}

export function platformLabel(code: string | null | undefined): string {
  if (!code) return "—";
  return PLATFORM_LABELS[code] ?? code;
}

export function platformColor(code: string | null | undefined, fallback = "#6b7280"): string {
  return code ? PLATFORM_COLORS[code] ?? fallback : fallback;
}

export function showHateTypeInCharts(code: string | null | undefined, showPolitical = false): boolean {
  return Boolean(code) && (showPolitical || !CHART_EXCLUDED_HATE_TYPES.has(String(code)));
}

export function platformGroup(code: string): "instant_messaging" | "social_network" {
  return MESSAGING_PLATFORMS.has(code) ? "instant_messaging" : "social_network";
}

export const PLATFORM_GROUP_LABELS: Record<string, string> = {
  social_network: "Plataformas sociais",
  instant_messaging: "Apps de mensagens",
};

/** Cores fixas por categoria (mesma legenda em todos os gráficos).
 *  Derivadas da paleta da identidade: vermelho, azul-escuro, preto e cinzas. */
export const CATEGORY_COLORS: Record<string, string> = {
  political: "#16305e",
  sexism: "#d92b3f",
  aporophobia: "#2f4a7a",
  religious_intolerance: "#8c1c2b",
  lgbtphobia: "#0b0f16",
  xenophobia: "#4a6fa5",
  capacitism: "#5b6880",
  racism: "#b01628",
  body_shame: "#6b7280",
  ageism: "#e0625a",
};
