/**
 * AtlasForge - Internship Assignment
 * Developer: Tejas Kamble
 * Email: tejaskgm1@gmail.com
 * Website: https://tejas-personal-portfolio-dev.vercel.app/
 * LinkedIn: https://www.linkedin.com/in/tejas-kamble-5342443b1
 * Instagram: tejask.co.in
 * GitHub: https://github.com/tejasworkspacews1-ui
 *
 * AtlasForge is a real-time intelligence dashboard that aggregates research papers,
 * news, jobs, and startup data from public APIs (arXiv, RSS feeds, RemoteOK, etc.)
 * with zero fabrication and zero cost. All data is freely accessible public data.
 */
const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`API ${res.status} ${path}`);
  return res.json() as Promise<T>;
}

export interface ModuleCounts {
  papers: number;
  startups: number;
  products: number;
  news: number;
  jobs: number;
}

export interface DashboardMetrics {
  total_records: number;
  records_last_24h: number;
  pipeline_health: number;
  freshness_score: number;
  by_module: ModuleCounts;
}

export interface PipelineRun {
  id: number;
  run_id: string;
  module: string;
  source: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  records_fetched: number;
  records_new: number;
  records_updated: number;
  records_failed: number;
  message: string | null;
}

export interface PageResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export const api = {
  health: () => http<{ status: string; service: string; time: string }>("/health"),
  dashboard: () => http<DashboardMetrics>("/dashboard"),
  listModule: <T>(
    module: "papers" | "startups" | "products" | "news" | "jobs",
    params: { page?: number; page_size?: number; q?: string } = {},
  ) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") qs.set(k, String(v));
    });
    return http<PageResult<T>>(`/${module}?${qs.toString()}`);
  },
  listRuns: (params: { page?: number; page_size?: number; module?: string } = {}) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") qs.set(k, String(v));
    });
    return http<PageResult<PipelineRun>>(`/pipeline/runs?${qs.toString()}`);
  },
};
