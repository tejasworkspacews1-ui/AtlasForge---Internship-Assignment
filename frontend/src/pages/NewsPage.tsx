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
import { Search, RefreshCw, ExternalLink, Clock, Sparkles } from "lucide-react";
import Panel from "../components/Panel";
import { api, NewsOut, PageResult } from "../lib/api";
import { formatRelative } from "../lib/utils";

export default function NewsPage() {
  const [page, setPage] = useState<PageResult<NewsOut> | null>(null);
  const [q, setQ] = useState("");
  const [online, setOnline] = useState<boolean | null>(null);
  const [triggering, setTriggering] = useState(false);
  const [lastTrigger, setLastTrigger] = useState<string | null>(null);
  const [showExtracted, setShowExtracted] = useState(false);

  const load = async (pageNum = 1) => {
    try {
      await api.health();
      setOnline(true);
      const res = await api.listModule<NewsOut>("news", { page: pageNum, page_size: 25, q });
      setPage(res);
    } catch {
      setOnline(false);
    }
  };

  useEffect(() => {
    load(1);
  }, []);

  const trigger = async (key: string) => {
    setTriggering(true);
    try {
      const res = await fetch(`/api/ingest/${key}`, { method: "POST" });
      const data = await res.json();
      if (key === "llm_enrich") {
        setLastTrigger(`llm_enrich: llm_hits=${data.llm_hits ?? 0} fallback_hits=${data.fallback_hits ?? 0} (of ${data.fetched})`);
      } else {
        setLastTrigger(`news: fetched=${data.fetched} new=${data.new} updated=${data.updated} stale_skipped=${data.stale_skipped ?? 0} failed=${data.failed}`);
      }
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
          <h1 className="text-2xl font-bold text-white tracking-tight">News Intelligence</h1>
          <p className="text-sm text-slate-500 mt-1">
            <Clock size={11} className="inline mr-1" />
            24-hour freshness rule — older items rejected at ingest time
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => trigger("news")}
            disabled={triggering}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 text-xs font-medium hover:bg-accent-cyan/20 disabled:opacity-50"
          >
            <RefreshCw size={12} className={triggering ? "animate-spin" : ""} />
            Fetch RSS
          </button>
          <button
            onClick={() => trigger("llm_enrich")}
            disabled={triggering}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-accent-violet/10 text-accent-violet border border-accent-violet/20 text-xs font-medium hover:bg-accent-violet/20 disabled:opacity-50"
          >
            <Sparkles size={12} />
            LLM Enrich
          </button>
          <label className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-slate-500">
            <input type="checkbox" checked={showExtracted} onChange={(e) => setShowExtracted(e.target.checked)} className="accent-accent-violet" />
            Show Extracted
          </label>
        </div>
      </header>

      {lastTrigger && (
        <div className="text-xs text-slate-400 bg-white/[0.02] border border-white/5 rounded-lg px-3 py-2 font-mono">
          {lastTrigger}
        </div>
      )}

      <Panel
        title="News Items"
        subtitle={online ? `${page?.total ?? 0} fresh items (≤24h) — page ${page?.page ?? 1}/${totalPages}` : "Backend offline"}
        right={
          <div className="relative">
            <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && load(1)}
              placeholder="Search news..."
              className="pl-8 pr-3 py-1.5 bg-obsidian-800 border border-white/10 rounded-lg text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-accent-cyan/40 w-64"
            />
          </div>
        }
      >
        {!page || page.items.length === 0 ? (
          <div className="space-y-2">
            <p className="text-sm text-slate-500">
              No news within the 24h window. Click <span className="text-accent-cyan">Fetch RSS</span> to ingest.
            </p>
          </div>
        ) : (
          <>
            <div className="space-y-2">
              {page.items.map((n) => (
                <div
                  key={n.id}
                  className="p-4 rounded-lg bg-white/[0.02] border border-white/5 hover:border-accent-cyan/30 transition-all"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="text-[10px] uppercase tracking-wider font-mono px-1.5 py-0.5 rounded bg-accent-violet/10 text-accent-violet border border-accent-violet/20">
                          {n.source}
                        </span>
                        {n.categories.slice(0, 2).map((c) => (
                          <span key={c} className="text-[10px] text-slate-500">{c}</span>
                        ))}
                        {n.extracted && (
                          <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
                            n.extracted.method === "llm"
                              ? "text-accent-violet bg-accent-violet/10 border-accent-violet/20"
                              : "text-accent-amber bg-accent-amber/10 border-accent-amber/20"
                          }`}>
                            {n.extracted.method === "llm" ? `LLM: ${n.extracted.provider}` : "fallback"}
                          </span>
                        )}
                      </div>
                      <a href={n.url} target="_blank" rel="noreferrer" className="text-sm font-medium text-white hover:text-accent-cyan flex items-center gap-1.5">
                        <span className="line-clamp-1">{n.title}</span>
                        <ExternalLink size={10} className="shrink-0 text-slate-500" />
                      </a>
                      {n.summary && <p className="text-xs text-slate-500 mt-1 line-clamp-2">{n.summary.replace(/<[^>]+>/g, "")}</p>}
                      {showExtracted && n.extracted && (
                        <div className="mt-2 p-2 rounded bg-obsidian-900/50 border border-white/5">
                          <ExtractedView data={n.extracted} />
                        </div>
                      )}
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xs text-slate-500">{n.published_at ? formatRelative(n.published_at) : "—"}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex items-center justify-between mt-4 text-xs text-slate-500">
              <span>{page.total} fresh · {page.items.length} shown</span>
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

function ExtractedView({ data }: { data: any }) {
  if (!data) return null;
  if (data.method === "deterministic") {
    return (
      <div className="text-xs space-y-1">
        {data.organizations?.length > 0 && (
          <div>
            <span className="text-slate-500 uppercase text-[10px] tracking-wider">Orgs:</span>{" "}
            {data.organizations.slice(0, 5).map((o: any, i: number) => (
              <span key={i} className="inline-block mr-2 text-slate-300">{o.name}</span>
            ))}
          </div>
        )}
        {data.urls?.length > 0 && (
          <div><span className="text-slate-500 uppercase text-[10px] tracking-wider">URLs:</span> <span className="text-accent-cyan font-mono text-[10px]">{data.urls.length}</span></div>
        )}
        {data.money_mentions?.length > 0 && (
          <div>
            <span className="text-slate-500 uppercase text-[10px] tracking-wider">Funding:</span>{" "}
            {data.money_mentions.map((m: any, i: number) => (
              <span key={i} className="inline-block mr-2 text-accent-emerald font-mono">{m.raw}</span>
            ))}
          </div>
        )}
      </div>
    );
  }
  const d = data.data;
  if (!d) return <div className="text-xs text-slate-500">No data extracted</div>;
  return (
    <div className="text-xs space-y-1">
      {Array.isArray(d.organizations) && d.organizations.length > 0 && (
        <div>
          <span className="text-slate-500 uppercase text-[10px] tracking-wider">Orgs:</span>{" "}
          {d.organizations.slice(0, 5).map((o: any, i: number) => (
            <span key={i} className="inline-block mr-2 text-slate-300">{o.name}</span>
          ))}
        </div>
      )}
      {Array.isArray(d.funding) && d.funding.length > 0 && (
        <div>
          <span className="text-slate-500 uppercase text-[10px] tracking-wider">Funding:</span>{" "}
          {d.funding.slice(0, 3).map((f: any, i: number) => (
            <span key={i} className="inline-block mr-2 text-accent-emerald font-mono">
              ${f.amount_usd}{f.unit || "M"}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
