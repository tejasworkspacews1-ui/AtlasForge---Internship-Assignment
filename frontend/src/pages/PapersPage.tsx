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
import { Search, Star, GitFork, ExternalLink, Github, RefreshCw } from "lucide-react";
import Panel from "../components/Panel";
import { api, PaperOut, PageResult } from "../lib/api";
import { formatRelative, formatNumber } from "../lib/utils";

export default function PapersPage() {
  const [page, setPage] = useState<PageResult<PaperOut> | null>(null);
  const [q, setQ] = useState("");
  const [online, setOnline] = useState<boolean | null>(null);
  const [triggering, setTriggering] = useState(false);
  const [lastTrigger, setLastTrigger] = useState<string | null>(null);

  const load = async (pageNum = 1) => {
    try {
      await api.health();
      setOnline(true);
      const res = await api.listModule<PaperOut>("papers", { page: pageNum, page_size: 25, q });
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
      setLastTrigger(`${key}: fetched=${data.fetched} new=${data.new} updated=${data.updated} failed=${data.failed}`);
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
          <h1 className="text-2xl font-bold text-white tracking-tight">Research Papers</h1>
          <p className="text-sm text-slate-500 mt-1">arXiv + GitHub enrichment (real data, no fabrication)</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => trigger("arxiv")}
            disabled={triggering}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 text-xs font-medium hover:bg-accent-cyan/20 disabled:opacity-50"
          >
            <RefreshCw size={12} className={triggering ? "animate-spin" : ""} />
            Fetch arXiv
          </button>
          <button
            onClick={() => trigger("github")}
            disabled={triggering}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-accent-violet/10 text-accent-violet border border-accent-violet/20 text-xs font-medium hover:bg-accent-violet/20 disabled:opacity-50"
          >
            <Github size={12} />
            Enrich GitHub
          </button>
        </div>
      </header>

      {lastTrigger && (
        <div className="text-xs text-slate-400 bg-white/[0.02] border border-white/5 rounded-lg px-3 py-2 font-mono">
          {lastTrigger}
        </div>
      )}

      <Panel
        title="Papers"
        subtitle={online ? `${formatNumber(page?.total ?? 0)} records — page ${page?.page ?? 1}/${totalPages}` : "Backend offline"}
        right={
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && load(1)}
                placeholder="Search title or abstract..."
                className="pl-8 pr-3 py-1.5 bg-obsidian-800 border border-white/10 rounded-lg text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-accent-cyan/40 w-64"
              />
            </div>
          </div>
        }
      >
        {!page || page.items.length === 0 ? (
          <p className="text-sm text-slate-500">
            No papers yet. Click <span className="text-accent-cyan">Fetch arXiv</span> above to ingest the latest from public arXiv categories (cs.AI, cs.LG, cs.CL, cs.CV, cs.RO, cs.IR, stat.ML). Then <span className="text-accent-violet">Enrich GitHub</span> to attach repo stars/forks.
          </p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-wider text-slate-500 border-b border-white/5">
                    <th className="py-2 font-medium">Title</th>
                    <th className="py-2 font-medium">Authors</th>
                    <th className="py-2 font-medium">Categories</th>
                    <th className="py-2 font-medium text-right">GitHub</th>
                    <th className="py-2 font-medium text-right">Published</th>
                  </tr>
                </thead>
                <tbody>
                  {page.items.map((p) => (
                    <tr key={p.id} className="border-b border-white/5 hover:bg-white/[0.02]">
                      <td className="py-3 max-w-md">
                        <a href={p.url} target="_blank" rel="noreferrer" className="text-white hover:text-accent-cyan font-medium flex items-center gap-1.5">
                          <span className="line-clamp-2">{p.title}</span>
                          <ExternalLink size={10} className="shrink-0" />
                        </a>
                        {p.abstract && <p className="text-xs text-slate-500 mt-1 line-clamp-1">{p.abstract}</p>}
                      </td>
                      <td className="py-3 text-slate-400 text-xs max-w-[180px]">
                         <div className="line-clamp-2">{(p.authors || []).slice(0, 3).join(", ")}{(p.authors || []).length > 3 ? ` +${(p.authors || []).length - 3}` : ""}</div>
                      </td>
                      <td className="py-3">
                        <div className="flex flex-wrap gap-1">
                           {(p.categories || []).slice(0, 3).map((c: string) => (
                            <span key={c} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20">
                              {c}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3 text-right">
                        {p.github_repo ? (
                          <div className="flex flex-col items-end gap-0.5">
                            <a href={`https://github.com/${p.github_repo}`} target="_blank" rel="noreferrer" className="text-accent-violet hover:underline text-xs font-mono">
                              {p.github_repo}
                            </a>
                            <div className="flex items-center gap-2 text-[10px] text-slate-500">
                              <span className="flex items-center gap-1"><Star size={10} className="text-accent-amber" />{formatNumber(p.github_stars ?? 0)}</span>
                              <span className="flex items-center gap-1"><GitFork size={10} />{formatNumber(p.github_forks ?? 0)}</span>
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-600">—</span>
                        )}
                      </td>
                      <td className="py-3 text-right text-slate-500 text-xs whitespace-nowrap">
                        {p.published_at ? formatRelative(p.published_at) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between mt-4 text-xs text-slate-500">
              <span>{page.total} total · {page.items.length} on this page</span>
              <div className="flex gap-2">
                <button
                  onClick={() => load(page.page - 1)}
                  disabled={page.page <= 1}
                  className="px-3 py-1.5 rounded bg-white/5 border border-white/10 disabled:opacity-30 hover:bg-white/10"
                >
                  Prev
                </button>
                <button
                  onClick={() => load(page.page + 1)}
                  disabled={page.page >= totalPages}
                  className="px-3 py-1.5 rounded bg-white/5 border border-white/10 disabled:opacity-30 hover:bg-white/10"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </Panel>
    </div>
  );
}
