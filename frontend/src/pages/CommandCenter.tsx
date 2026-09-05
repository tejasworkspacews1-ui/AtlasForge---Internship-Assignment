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
import {
  Activity, Database, Zap, Clock, AlertCircle, FileText, Building2,
  Cpu, Newspaper, Briefcase,
} from "lucide-react";
import {
  AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import StatCard from "../components/StatCard";
import Panel from "../components/Panel";
import { api, DashboardMetrics, PipelineRun } from "../lib/api";
import { formatNumber, formatRelative } from "../lib/utils";

const statusStyles: Record<string, string> = {
  success: "text-accent-emerald bg-accent-emerald/10 border-accent-rose/20",
};
function statusClass(s: string) {
  if (s === "success") return "text-accent-emerald bg-accent-emerald/10 border-accent-emerald/20";
  if (s === "failed") return "text-accent-rose bg-accent-rose/10 border-accent-rose/20";
  if (s === "running") return "text-accent-cyan bg-accent-cyan/10 border-accent-cyan/20";
  return "text-accent-amber bg-accent-amber/10 border-accent-amber/20";
}

const COLORS: Record<string, string> = {
  Papers: "#22d3ee", News: "#a78bfa", Products: "#34d399", Jobs: "#fbbf24", Startups: "#fb7185",
};

const EMPTY_DASH: DashboardMetrics = {
  total_records: 0,
  records_last_24h: 0,
  pipeline_health: 100,
  freshness_score: 100,
  by_module: { papers: 0, startups: 0, products: 0, news: 0, jobs: 0 },
};

export default function CommandCenter() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [online, setOnline] = useState<boolean | null>(null);
  const [hours, setHours] = useState<{ hour: string; records: number }[]>([]);

  useEffect(() => {
    (async () => {
      try {
        await api.health();
        setOnline(true);
        const [dash, runPage] = await Promise.all([api.dashboard(), api.listRuns({ page_size: 5 })]);
        setMetrics(dash);
        setRuns(runPage.items);
        const buckets: Record<number, number> = {};
        for (const r of runPage.items) {
          const h = new Date(r.started_at).getHours();
          buckets[h] = (buckets[h] || 0) + r.records_new;
        }
        const h24 = Array.from({ length: 24 }, (_, i) => ({ hour: `${String(i).padStart(2, "0")}h`, records: buckets[i] || 0 }));
        setHours(h24);
      } catch {
        setOnline(false);
      }
    })();
  }, []);

  const dash = metrics ?? EMPTY_DASH;
  const isDemo = online === null || online === false || dash.total_records === 0;
  const moduleData = [
    { name: "Papers", value: dash.by_module.papers },
    { name: "News", value: dash.by_module.news },
    { name: "Products", value: dash.by_module.products },
    { name: "Jobs", value: dash.by_module.jobs },
    { name: "Startups", value: dash.by_module.startups },
  ];

  return (
    <div className="p-8 space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Command Center</h1>
          <p className="text-sm text-slate-500 mt-1">
             {online ? "Local data from local SQLite + FastAPI" : "Backend offline — start the API to see local data"}
          </p>
        </div>
        {isDemo && (
          <span className="text-[10px] uppercase tracking-widest px-3 py-1.5 rounded-full bg-accent-amber/10 text-accent-amber border border-accent-amber/20">
            No Records Yet — Phase B
          </span>
        )}
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Records" value={formatNumber(dash.total_records)} delta={online ? `+${dash.records_last_24h} in last 24h` : "—"} icon={<Database size={16} />} accent="cyan" />
        <StatCard label="Pipeline Health" value={`${dash.pipeline_health}%`} delta="5 modules active" icon={<Activity size={16} />} accent="emerald" />
        <StatCard label="Freshness (24h)" value={`${dash.freshness_score}%`} delta="4/5 modules fresh" icon={<Clock size={16} />} accent="violet" />
        <StatCard label="Records / Hour" value="—" delta="After first ingest" icon={<Zap size={16} />} accent="amber" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Pipeline Activity (24h)" subtitle="New records per hour from last 5 runs" className="lg:col-span-2">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={hours}>
                <defs>
                  <linearGradient id="recs" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="hour" stroke="#475569" fontSize={10} />
                <YAxis stroke="#475569" fontSize={10} />
                <Tooltip contentStyle={{ background: "#0f1422", border: "1px solid #1c2440", borderRadius: 8 }} />
                <Area type="monotone" dataKey="records" stroke="#22d3ee" fill="url(#recs)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Records by Module">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={moduleData} dataKey="value" innerRadius={50} outerRadius={80} paddingAngle={2}>
                  {moduleData.map((m, i) => (
                    <Cell key={i} fill={COLORS[m.name]} stroke="#0a0e18" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#0f1422", border: "1px solid #1c2440", borderRadius: 8 }} />
                <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Module Counts" className="lg:col-span-1">
          <div className="space-y-2">
            {moduleData.map((m) => (
              <div key={m.name} className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02] border border-white/5">
                <div className="flex items-center gap-3">
                  <span className="w-2 h-2 rounded-full" style={{ background: COLORS[m.name] }} />
                  <span className="text-sm text-slate-300">{m.name}</span>
                </div>
                <span className="text-sm font-mono text-white">{formatNumber(m.value)}</span>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Recent Pipeline Runs" subtitle={online ? "From local database" : "Run an ingestor to populate"} className="lg:col-span-2">
          {runs.length === 0 ? (
            <p className="text-sm text-slate-500">No pipeline runs yet. Phase C will add real ingestors.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-wider text-slate-500 border-b border-white/5">
                    <th className="py-2 font-medium">Run ID</th>
                    <th className="py-2 font-medium">Module</th>
                    <th className="py-2 font-medium">Source</th>
                    <th className="py-2 font-medium">Status</th>
                    <th className="py-2 font-medium text-right">New</th>
                    <th className="py-2 font-medium text-right">When</th>
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
                      <td className="py-3 text-right font-mono text-white">{r.records_new}</td>
                      <td className="py-3 text-right text-slate-500 text-xs">{formatRelative(r.started_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>

      <Panel
        title="System Status"
        right={
          <span className={`text-[10px] uppercase flex items-center gap-1.5 ${online ? "text-accent-emerald" : "text-accent-amber"}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${online ? "bg-accent-emerald animate-pulse" : "bg-accent-amber"}`} />
            {online ? "Backend Online" : "Backend Offline"}
          </span>
        }
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {[
            { label: "Database", value: online ? "SQLite (local) — connected" : "SQLite (local) — pending", ok: online },
             { label: "API Server", value: online ? "FastAPI :8000 — running" : "FastAPI :8000 — not started", ok: online },
            { label: "arXiv Ingestor", value: "Phase C", ok: false },
            { label: "LLM Engine", value: "Phase E", ok: false },
          ].map((s) => (
            <div key={s.label} className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
              <div className="flex items-center gap-2 mb-1">
                {s.ok ? <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald" /> : <AlertCircle size={12} className="text-accent-amber" />}
                <span className="text-xs text-slate-500">{s.label}</span>
              </div>
              <div className="text-white text-xs font-medium">{s.value}</div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
