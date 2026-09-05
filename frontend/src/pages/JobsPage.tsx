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
import { useEffect, useState } from "react";
import { Search, RefreshCw, ExternalLink, MapPin, Briefcase } from "lucide-react";
import Panel from "../components/Panel";
import { api, JobOut, PageResult } from "../lib/api";
import { formatRelative } from "../lib/utils";

export default function JobsPage() {
  const [page, setPage] = useState<PageResult<JobOut> | null>(null);
  const [q, setQ] = useState("");
  const [online, setOnline] = useState<boolean | null>(null);
  const [triggering, setTriggering] = useState(false);
  const [lastTrigger, setLastTrigger] = useState<string | null>(null);

  const load = async (pageNum = 1) => {
    try {
      await api.health();
      setOnline(true);
      const res = await api.listModule<JobOut>("jobs", { page: pageNum, page_size: 25, q });
      setPage(res);
    } catch {
      setOnline(false);
    }
  };

  useEffect(() => {
    load(1);
  }, []);

  const trigger = async () => {
    setTriggering(true);
    try {
      const res = await fetch(`/api/ingest/jobs`, { method: "POST" });
      const data = await res.json();
      setLastTrigger(`jobs: fetched=${data.fetched} new=${data.new} updated=${data.updated} failed=${data.failed} (window=${data.freshness_window_hours}h)`);
      await load(1);
    } catch (e) {
      setLastTrigger(`Error: ${(e as Error).message}`);
    } finally {
      setTriggering(false);
    }
  };

  const totalPages = page ? Math.max(1, Math.ceil(page.total / page.page_size)) : 1;

  return (
    <div className="p-8 space-y-6">
      <header className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Jobs</h1>
          <p className="text-sm text-slate-500 mt-1">
            <Briefcase size={11} className="inline mr-1" />
            AI-tagged roles from RemoteOK + Arbeitnow — freshness enforced at ingest
          </p>
        </div>
        <button
          onClick={trigger}
          disabled={triggering}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-accent-amber/10 text-accent-amber border border-accent-amber/20 text-xs font-medium hover:bg-accent-amber/20 disabled:opacity-50"
        >
          <RefreshCw size={12} className={triggering ? "animate-spin" : ""} />
          Fetch Jobs
        </button>
      </header>

      {lastTrigger && (
        <div className="text-xs text-slate-400 bg-white/[0.02] border border-white/5 rounded-lg px-3 py-2 font-mono">
          {lastTrigger}
        </div>
      )}

      <Panel
        title="Job Postings"
        subtitle={online ? `${page?.total ?? 0} active roles — page ${page?.page ?? 1}/${totalPages}` : "Backend offline"}
        right={
          <div className="relative">
            <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && load(1)}
              placeholder="Search jobs..."
              className="pl-8 pr-3 py-1.5 bg-obsidian-800 border border-white/10 rounded-lg text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-accent-cyan/40 w-64"
            />
          </div>
        }
      >
        {!page || page.items.length === 0 ? (
          <div className="space-y-2">
            <p className="text-sm text-slate-500">
              No AI jobs in current window. Click <span className="text-accent-amber">Fetch Jobs</span> — the system filters RemoteOK + Arbeitnow for AI/ML titles within the configured freshness window.
            </p>
            <p className="text-xs text-slate-600">
              If the result is 0, it's because no AI-tagged jobs were posted on those public feeds within the window — that's an honest real-time signal, not a bug.
            </p>
          </div>
        ) : (
          <>
            <div className="space-y-2">
              {page.items.map((j) => (
                <a
                  key={j.id}
                  href={j.url}
                  target="_blank"
                  rel="noreferrer"
                  className="block p-4 rounded-lg bg-white/[0.02] border border-white/5 hover:border-accent-amber/30 hover:bg-white/[0.04] transition-all"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] uppercase tracking-wider font-mono px-1.5 py-0.5 rounded bg-accent-amber/10 text-accent-amber border border-accent-amber/20">
                          {j.source}
                        </span>
                        <span className="text-xs text-slate-300">{j.company}</span>
                      </div>
                      <h3 className="text-sm font-medium text-white flex items-center gap-1.5">
                        <span className="line-clamp-1">{j.title}</span>
                        <ExternalLink size={10} className="shrink-0 text-slate-500" />
                      </h3>
                      <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                        <span className="flex items-center gap-1"><MapPin size={10} />{j.location || "Remote"}</span>
                        {(j.salary_min || j.salary_max) && (
                          <span className="font-mono text-accent-emerald">
                            {j.salary_min ? `$${Math.round(j.salary_min/1000)}k` : ""}
                            {j.salary_min && j.salary_max ? "–" : ""}
                            {j.salary_max ? `$${Math.round(j.salary_max/1000)}k` : ""}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right shrink-0 text-xs text-slate-500">
                      {j.posted_at ? formatRelative(j.posted_at) : "—"}
                    </div>
                  </div>
                </a>
              ))}
            </div>
            <div className="flex items-center justify-between mt-4 text-xs text-slate-500">
              <span>{page.total} total · {page.items.length} shown</span>
              <div className="flex gap-2">
                <button onClick={() => load(page.page - 1)} disabled={page.page <= 1} className="px-3 py-1.5 rounded bg-white/5 border border-white/10 disabled:opacity-30 hover:bg-white/10">Prev</button>
                <button onClick={() => load(page.page + 1)} disabled={page.page >= totalPages} className="px-3 py-1.5 rounded bg-white/5 border border-white/10 disabled:opacity-30 hover:bg-white/10">Next</button>
              </div>
            </div>
          </>
        )}
      </Panel>
    </div>
  );
}
