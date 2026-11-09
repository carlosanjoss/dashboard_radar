import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import Fastify from "fastify";
import fastifyStatic from "@fastify/static";
import { ping } from "./db.ts";
import { parseFilters, type FilterInput } from "./queries.ts";
import * as Q from "./queries.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const DIST = resolve(HERE, "..", "dist");
const PORT = Number(process.env.API_PORT ?? 8787);

const app = Fastify({ logger: { level: "info" } });

type Req = { query: Record<string, unknown> };

function filtersFrom(query: Record<string, unknown>) {
  return parseFilters(query as FilterInput);
}

function int(value: unknown, fallback: number, min: number, max: number): number {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(Math.max(Math.trunc(n), min), max);
}

const routes: Array<[string, (req: Req) => Promise<unknown>]> = [
  ["/api/health", async () => ({ ok: true, db: await ping() })],
  ["/api/meta", async () => Q.getMeta()],
  ["/api/overview", async (req) => Q.getOverview(filtersFrom(req.query))],
  ["/api/platforms", async (req) => Q.getPlatforms(filtersFrom(req.query))],
  ["/api/categories", async (req) => Q.getCategories(filtersFrom(req.query))],
  ["/api/category-probabilities", async (req) => Q.getCategoryProbabilities(filtersFrom(req.query))],
  ["/api/temporal", async (req) => Q.getTemporal(filtersFrom(req.query), String(req.query.grain ?? "day"))],
  [
    "/api/toxicity",
    async (req) =>
      Q.getToxicity(
        filtersFrom(req.query),
        String(req.query.grain ?? "month"),
        int(req.query.limit, 10, 1, 20),
      ),
  ],
  ["/api/terms", async (req) => Q.getTerms(filtersFrom(req.query), int(req.query.limit, 60, 5, 200))],
  [
    "/api/network",
    async (req) =>
      Q.getNetwork(
        filtersFrom(req.query),
        int(req.query.limit, 200, 10, 600),
        int(req.query.minWeight, 5, 1, 10_000),
      ),
  ],
  [
    "/api/authors",
    async (req) =>
      Q.getAuthors(
        filtersFrom(req.query),
        int(req.query.limit, 100, 5, 500),
        int(req.query.minRecords, 3, 1, 100),
      ),
  ],
  [
    "/api/posts",
    async (req) =>
      Q.getPosts(
        filtersFrom(req.query),
        int(req.query.limit, 100, 5, 500),
        int(req.query.minRecords, 2, 1, 100),
      ),
  ],
  [
    "/api/records",
    async (req) =>
      Q.getRecords(
        filtersFrom(req.query),
        int(req.query.page, 1, 1, 1_000_000),
        int(req.query.pageSize, 25, 5, 200),
      ),
  ],
  ["/api/quality", async (req) => Q.getQuality(filtersFrom(req.query))],
  ["/api/intersectionality", async (req) => Q.getIntersectionality(filtersFrom(req.query))],
  [
    "/api/threads",
    async (req) => Q.getThreads(filtersFrom(req.query), int(req.query.limit, 15, 5, 50)),
  ],
  ["/api/threshold", async (req) => Q.getThreshold(filtersFrom(req.query))],
];

for (const [path, handler] of routes) {
  app.get(path, async (req, reply) => {
    try {
      return await handler(req as Req);
    } catch (error) {
      req.log.error({ err: error }, `falha em ${path}`);
      reply.code(500);
      return { error: error instanceof Error ? error.message : String(error) };
    }
  });
}

app.get<{ Params: { key: string } }>("/api/records/post/:key", async (req, reply) => {
  try {
    const filters = filtersFrom(req.query as Record<string, unknown>);
    return await Q.getRecordsForPost(
      req.params.key,
      filters,
      int((req.query as Record<string, unknown>).page, 1, 1, 1_000_000),
      int((req.query as Record<string, unknown>).pageSize, 50, 5, 200),
    );
  } catch (error) {
    req.log.error({ err: error }, "falha em /api/records/post/:key");
    reply.code(500);
    return { error: error instanceof Error ? error.message : String(error) };
  }
});

if (existsSync(DIST)) {
  await app.register(fastifyStatic, { root: DIST });
  app.setNotFoundHandler((req, reply) => {
    if (req.raw.url?.startsWith("/api/")) {
      reply.code(404).send({ error: "rota não encontrada" });
      return;
    }
    reply.sendFile("index.html");
  });
}

app
  .listen({ port: PORT, host: "0.0.0.0" })
  .then(() => app.log.info(`API Radar em http://127.0.0.1:${PORT}`))
  .catch((error) => {
    app.log.error(error);
    process.exit(1);
  });