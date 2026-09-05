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
import { Search, GitMerge, Sparkles, ChevronDown, ChevronUp } from "lucide-react";
import Panel from "../components/Panel";

interface Alias {
  alias: string;
  confidence: number;
  reasoning: string | null;
}

interface Cluster {
  id: number;
  canonical: string;
  kind: string;
  confidence: number;
  alias_count: number;
  aliases: Alias[];
}

export default function EntityResolutionPage() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [q, setQ] = useState("");
  const [online, setOnline] = useState<boolean | null>(null);
  const [triggering, setTriggering] = useState(false);
  const [lastTrigger, setLastTrigger] = useState<string | null>(null);
  const [testName, setTestName] = useState("Open AI");
  const [resolveResult, setResolveResult] = useState<any | null>(null);
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  const load = async () => {
    try {
      await fetch("/api/health");
      setOnline(true);
      const res = await fetch(`/api/entities/clusters?page_size=100&q=${encodeURIComponent(q)}`);
      const data = await res.json();
      setClusters(data.items || []);
    } catch {
      setOnline(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [q]);

  const trigger = async () => {
    setTriggering(true);
    try {
      const res = await fetch("/api/ingest/entity_resolution", { method: "POST" });
      const data = await res.json();
      setLastTrigger(`entity_resolution: resolved=${data.resolved} new_entities=${data.new_entities} new_aliases=${data.new_aliases}`);
      await load();
    } catch (e) {
      setLastTrigger(`Error: ${(e as Error).message}`);
    } finally {
      setTriggering(false);
    }
  };

  const testResolve = async () => {
    try {
      const res = await fetch("/api/entities/resolve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: testName }),
      });
      setResolveResult(await res.json());
    } catch (e) {
      setResolveResult({ error: (e as Error).message });
    }
  };

  const methodColor = (m: string) => {
    if (m.startsWith("seed") || m === "db_exact") return "text-accent-emerald bg-accent-emerald/10 border-accent-emerald/20";
    if (m === "fuzzy") return "text-accent-cyan bg-accent-cyan/10 border-accent-cyan/20";
    if (m === "new") return "text-accent-amber bg-accent-amber/10 border-accent-amber/20";
    return "text-slate-400 bg-white/5 border-white/10";
  };

  return (
    <div className="p-8 space-y-6">
      <header className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Entity Resolution</h1>
          <p className="text-sm text-slate-500 mt-1">
            <GitMerge size={11} className="inline mr-1" />
            3-tier normalization: seed dictionary → fuzzy match → LLM assist
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={trigger}
            disabled={triggering}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-accent-violet/10 text-accent-violet border border-accent-violet/20 text-xs font-medium hover:bg-accent-violet/20 disabled:opacity-50"
          >
            <Sparkles size={12} />
            {triggering ? "Resolving…" : "Run Resolution"}
          </button>
        </div>
      </header>

      {lastTrigger && (
        <div className="text-xs text-slate-400 bg-white/[0.02] border border-white/5 rounded-lg px-3 py-2 font-mono">
          {lastTrigger}
        </div>
      )}

      <Panel
        title="Test Resolver"
        subtitle="Try any company name. Try 'Open AI', 'DeepMind', 'FAIR', 'NVIDIA'"
      >
        <div className="flex items-center gap-2">
          <input
            value={testName}
            onChange={(e) => setTestName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && testResolve()}
            placeholder="Type a company name…"
            className="flex-1 px-3 py-2 bg-obsidian-800 border border-white/10 rounded-lg text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-accent-violet/40"
          />
          <button
            onClick={testResolve}
            className="px-4 py-2 rounded-lg bg-accent-violet/20 text-accent-violet border border-accent-violet/30 text-sm font-medium hover:bg-accent-violet/30"
          >
            Resolve
          </button>
        </div>
        {resolveResult && (
          <div className="mt-3 p-3 rounded-lg bg-obsidian-900/50 border border-white/5">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs text-slate-500">Input:</span>
              <span className="text-sm font-mono text-slate-300">"{resolveResult.input}"</span>
              <span className="text-slate-600">→</span>
              <span className="text-sm font-bold text-white">{resolveResult.canonical}</span>
              <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${methodColor(resolveResult.method)}`}>
                {resolveResult.method} · {Math.round(resolveResult.confidence * 100)}%
              </span>
            </div>
            <p className="text-xs text-slate-400">{resolveResult.reasoning}</p>
          </div>
        )}
      </Panel>

      <Panel
        title={`Canonical Clusters (${clusters.length})`}
        subtitle="Each cluster groups all known aliases under one canonical name"
        right={
          <div className="relative">
            <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Filter…"
              className="pl-8 pr-3 py-1.5 bg-obsidian-800 border border-white/10 rounded-lg text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-accent-violet/40 w-48"
            />
          </div>
        }
      >
        {clusters.length === 0 ? (
          <p className="text-sm text-slate-500">
            No clusters yet. Click <span className="text-accent-violet">Run Resolution</span> to process extracted orgs from news items.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {clusters.map((c) => {
              const isOpen = expanded[c.id];
              const methodTag = c.aliases.length > 0
                ? c.aliases[0].reasoning?.split(":")[0] || "seed"
                : "new";
              return (
                <div key={c.id} className="p-4 rounded-lg bg-white/[0.02] border border-white/5 hover:border-accent-violet/30 transition-all">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <GitMerge size={14} className="text-accent-violet shrink-0" />
                      <span className="font-semibold text-white truncate">{c.canonical}</span>
                      <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${methodColor(methodTag)}`}>
                        {c.alias_count} alias{c.alias_count === 1 ? "" : "es"}
                      </span>
                    </div>
                    {c.aliases.length > 0 && (
                      <button
                        onClick={() => setExpanded({ ...expanded, [c.id]: !isOpen })}
                        className="text-slate-500 hover:text-white"
                      >
                        {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </button>
                    )}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    Kind: {c.kind} · Confidence: {Math.round(c.confidence * 100)}%
                  </div>
                  {isOpen && c.aliases.length > 0 && (
                    <div className="mt-3 space-y-1.5 pt-3 border-t border-white/5">
                      {c.aliases.map((a, i) => (
                        <div key={i} className="flex items-center justify-between text-xs">
                          <span className="font-mono text-slate-300">{a.alias}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-slate-500">{Math.round(a.confidence * 100)}%</span>
                            <span className="text-[10px] text-slate-600 truncate max-w-[180px]" title={a.reasoning || ""}>
                              {a.reasoning?.split(":").slice(1).join(":").trim().slice(0, 40)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Panel>
    </div>
  );
}
