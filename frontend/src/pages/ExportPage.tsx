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
import { Download, FileText, FileSpreadsheet, Database, CheckCircle2 } from "lucide-react";
import Panel from "../components/Panel";

interface ExportModule {
  key: string;
  rows: number;
  cols: number;
  formats: string[];
}

export default function ExportPage() {
  const [exports, setExports] = useState<ExportModule[]>([]);
  const [online, setOnline] = useState<boolean | null>(null);
  const [totals, setTotals] = useState<Record<string, number>>({});
  const [downloaded, setDownloaded] = useState<Record<string, boolean>>({});

  const load = async () => {
    try {
      await fetch("/api/health");
      setOnline(true);
      const res = await fetch("/api/export/available");
      const data = await res.json();
      const counts = await fetch("/api/dashboard").then((r) => r.json()).catch(() => null);
      const t: Record<string, number> = {};
      if (counts?.by_module) {
        t.papers = counts.by_module.papers;
        t.startups = counts.by_module.startups;
        t.products = counts.by_module.products;
        t.news = counts.by_module.news;
        t.jobs = counts.by_module.jobs;
      }
      try {
        const ent = await fetch("/api/entities/clusters?page_size=1").then((r) => r.json());
        t.entities = ent.total;
      } catch {}
      setTotals(t);
      setExports(
        data.modules.map((m: string) => ({
          key: m,
          rows: t[m] ?? 0,
          cols: data.column_counts[m],
          formats: data.formats,
        }))
      );
    } catch {
      setOnline(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDownload = (mod: string, fmt: string) => {
    const url = `/api/export/${mod}.${fmt}`;
    const a = document.createElement("a");
    a.href = url;
    a.download = "";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setDownloaded({ ...downloaded, [`${mod}.${fmt}`]: true });
  };

  return (
    <div className="p-8 space-y-6">
      <header className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Export Center</h1>
          <p className="text-sm text-slate-500 mt-1">
            <Download size={11} className="inline mr-1" />
            CSV (RFC 4180) + TSV (Google Sheets paste-ready) per module
          </p>
        </div>
      </header>

      <Panel
        title="Available Exports"
        subtitle={online ? "Direct download from FastAPI — no intermediate storage" : "Backend offline"}
        right={
          <span className={`text-[10px] uppercase flex items-center gap-1.5 ${online ? "text-accent-emerald" : "text-accent-amber"}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${online ? "bg-accent-emerald animate-pulse" : "bg-accent-amber"}`} />
            {online ? "Local" : "Offline"}
          </span>
        }
      >
        {exports.length === 0 ? (
          <p className="text-sm text-slate-500">No modules available.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {exports.map((m) => (
              <div key={m.key} className="p-4 rounded-lg bg-white/[0.02] border border-white/5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Database size={14} className="text-accent-cyan" />
                    <span className="font-semibold text-white capitalize">{m.key}</span>
                    <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20">
                      {m.rows} row{m.rows === 1 ? "" : "s"}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500">{m.cols} columns</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => handleDownload(m.key, "csv")}
                    disabled={!online}
                    className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 text-xs font-medium hover:bg-accent-cyan/20 disabled:opacity-30"
                  >
                    {downloaded[`${m.key}.csv`] ? <CheckCircle2 size={12} /> : <FileText size={12} />}
                    Download CSV
                  </button>
                  <button
                    onClick={() => handleDownload(m.key, "tsv")}
                    disabled={!online}
                    className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/20 text-xs font-medium hover:bg-accent-emerald/20 disabled:opacity-30"
                  >
                    {downloaded[`${m.key}.tsv`] ? <CheckCircle2 size={12} /> : <FileSpreadsheet size={12} />}
                    Download TSV
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Panel>

      <Panel title="How to use" subtitle="End-to-end export workflow">
        <ol className="text-sm text-slate-400 space-y-2 list-decimal pl-5">
          <li>
            Click <span className="text-accent-cyan font-medium">Download CSV</span> for any module — files are RFC-4180 compliant and open cleanly in Excel, Numbers, and Pandas.
          </li>
          <li>
            Click <span className="text-accent-emerald font-medium">Download TSV</span> for Google Sheets paste workflow: open a new sheet, click cell A1, paste — the entire table fills in cleanly with one row per record.
          </li>
          <li>
            All timestamps are ISO 8601 UTC. All entity references use canonical names (e.g., <code className="text-accent-violet">OpenAI</code>, not <code className="text-slate-500">"Open AI"</code>).
          </li>
          <li>
            File names follow <code className="text-slate-300">atlasforge_&lt;module&gt;_&lt;timestamp&gt;.&lt;ext&gt;</code>.
          </li>
        </ol>
      </Panel>
    </div>
  );
}
