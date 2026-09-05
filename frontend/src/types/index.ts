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
export type DataModule = "papers" | "startups" | "products" | "news" | "jobs";

export interface PipelineRun {
  id: string;
  module: DataModule;
  status: "running" | "success" | "failed" | "pending";
  startedAt: string;
  finishedAt?: string;
  recordsFetched: number;
  recordsNew: number;
  recordsFailed: number;
  source: string;
  message?: string;
}

export interface EntityCluster {
  canonical: string;
  aliases: string[];
  confidence: number;
  reasoning: string;
  count: number;
}

export interface DashboardMetrics {
  totalRecords: number;
  recordsLast24h: number;
  pipelineHealth: number;
  freshnessScore: number;
  byModule: Record<DataModule, number>;
}
