import { readFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import pg from "pg";
import { Pool, type QueryResultRow } from "pg";
import dotenv from "dotenv";

// DATE (OID 1082) volta como string "YYYY-MM-DD" — evita shift de timezone.
pg.types.setTypeParser(1082, (value: string) => value);

const HERE = dirname(fileURLToPath(import.meta.url));
export const PROJECT_DIR = resolve(HERE, "..", "..");

/** .env do próprio dashboard (opcional). */
dotenv.config({ path: resolve(HERE, "..", ".env") });

function parseEnvFile(path: string): Record<string, string> {
  const out: Record<string, string> = {};
  if (!existsSync(path)) return out;
  for (const rawLine of readFileSync(path, "utf8").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    out[key] = value;
  }
  return out;
}

/** .env oficial do pipeline Radar Ódio (banco compartilhado). */
function pipelineEnv(): Record<string, string> {
  const candidates = [
    resolve(PROJECT_DIR, "social_data_pipeline", ".env"),
    resolve(PROJECT_DIR, "Trabalho Radar Ódio", "social_data_pipeline", ".env"),
  ];
  for (const path of candidates) {
    const values = parseEnvFile(path);
    if (values.POSTGRES_URI) return values;
  }
  return {};
}

function connectionString(): string {
  if (process.env.DATABASE_URL) return process.env.DATABASE_URL;
  const pipeline = pipelineEnv();
  if (pipeline.POSTGRES_URI) return pipeline.POSTGRES_URI;

  const host = process.env.DB_HOST ?? "localhost";
  const port = process.env.DB_PORT ?? pipeline.POSTGRES_PORT ?? "5433";
  const user = process.env.DB_USER ?? pipeline.POSTGRES_USER ?? "radar";
  const password = process.env.DB_PASSWORD ?? pipeline.POSTGRES_PASSWORD ?? "admin123";
  const database = process.env.DB_NAME ?? pipeline.POSTGRES_DB ?? "radar_odio";
  return `postgresql://${user}:${password}@${host}:${port}/${database}`;
}

export const pool = new Pool({
  connectionString: connectionString(),
  max: 8,
  idleTimeoutMillis: 30_000,
  options: "-c max_parallel_workers_per_gather=0",
});

/** Janela analisada pelo painel (período eleições 1º turno). */
export const DASHBOARD_MIN_DATE = process.env.DASHBOARD_MIN_DATE ?? "2026-09-01";
export const MODEL_NAME = process.env.MODEL_NAME ?? "radarodio-v01-bert";

export async function q<T extends QueryResultRow = QueryResultRow>(
  sql: string,
  params: unknown[] = [],
): Promise<T[]> {
  const result = await pool.query<T>(sql, params as never[]);
  return result.rows;
}

export async function one<T extends QueryResultRow = QueryResultRow>(
  sql: string,
  params: unknown[] = [],
): Promise<T | undefined> {
  return (await q<T>(sql, params))[0];
}

export async function ping(): Promise<string> {
  const row = await one<{ db: string; usr: string }>(
    "SELECT current_database() AS db, current_user AS usr",
  );
  return `${row?.db}@${row?.usr}`;
}