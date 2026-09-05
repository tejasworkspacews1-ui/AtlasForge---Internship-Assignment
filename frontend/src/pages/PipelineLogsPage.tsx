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
import Panel from "../components/Panel";
import { api, PipelineRun } from "../lib/api";
import { formatRelative } from "../lib/utils";

function statusClass(s: string) {
  if (s === "success") return "text-accent-emerald bg-accent-emerald/10 border-accent-emerald/20";
  if (s === "failed") return "text-accent-rose bg-accent-rose/10 border-accent-rose/20";
  if (s === "running") return "text-accent-cyan bg-accent-cyan/10 border-accent-cyan/20";
  return "text-accent-amber bg-accent-amber/10 border-accent-amber/20";
}

export default function PipelineLogsPage() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    (async () => {
      try {
        await api.health();
        setOnline(true);
        const r = await api.listRuns({ page_size: 50 });
        setRuns(r.items);
      } catch {
        setOnline(false);
      }
    })();
  }, []);

  return (
    <div className="p-8">
      <Panel
        title="Pipeline Logs"
        subtitle={online ? "Last 50 runs from local database" : "Start the backend to view logs"}
        right={
          <span className={`text-[10px] uppercase flex items-center gap-1.5 ${online ? "text-accent-emerald" : "text-accent-amber"}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${online ? "bg-accent-emerald animate-pulse" : "bg-accent-amber"}`} />
            {online ? "Local" : "Offline"}
          </span>
        }
      >
        {runs.length === 0 ? (
          <p className="text-sm text-slate-500">No pipeline runs recorded yet. Phase C will start populating this view.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[10px] uppercase tracking-wider text-slate-500 border-b border-white/5">
                  <th className="py-2 font-medium">Run</th>
                  <th className="py-2 font-medium">Module</th>
                  <th className="py-2 font-medium">Source</th>
                  <th className="py-2 font-medium">Status</th>
                  <th className="py-2 font-medium text-right">Fetched</th>
                  <th className="py-2 font-medium text-right">New</th>
                  <th className="py-2 font-medium text-right">Failed</th>
                  <th className="py-2 font-medium text-right">Started</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr key={r.run_id} className="border-b border-white/5 hover:bg-white/[0.02]">
                    <td className="py-3 font-mono text-xs text-slate-400">{r.run_id}</td>
                    <td className="py-3 capitalize text-slate-300">{r.module}</td>
                    <td className="py-3 text-slate-400">{r.source}</td>
                    <td className="py-3">
                      <span className={`text-[10px] uppercase tracking-wider px-2 py-1 rounded border ${statusClass(r.status)}`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="py-3 text-right font-mono text-white">{r.records_fetched}</td>
                    <td className="py-3 text-right font-mono text-accent-emerald">{r.records_new}</td>
                    <td className="py-3 text-right font-mono text-accent-rose">{r.records_failed}</td>
                    <td className="py-3 text-right text-slate-500 text-xs">{formatRelative(r.started_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </div>
  );
}
