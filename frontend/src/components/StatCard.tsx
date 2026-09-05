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
import { ReactNode } from "react";
import { cn } from "../lib/utils";

export default function StatCard({
  label,
  value,
  delta,
  icon,
  accent = "cyan",
}: {
  label: string;
  value: string | number;
  delta?: string;
  icon: ReactNode;
  accent?: "cyan" | "violet" | "amber" | "emerald" | "rose";
}) {
  const accents = {
    cyan: "from-accent-cyan/20 to-transparent text-accent-cyan",
    violet: "from-accent-violet/20 to-transparent text-accent-violet",
    amber: "from-accent-amber/20 to-transparent text-accent-amber",
    emerald: "from-accent-emerald/20 to-transparent text-accent-emerald",
    rose: "from-accent-rose/20 to-transparent text-accent-rose",
  };
  return (
    <div className="glass rounded-xl p-5 glass-hover relative overflow-hidden">
      <div className={cn("absolute inset-0 bg-gradient-to-br opacity-50", accents[accent])} />
      <div className="relative">
        <div className="flex items-center justify-between">
          <span className="metric-label">{label}</span>
          <div className={cn("p-2 rounded-lg bg-white/5", accents[accent].split(" ")[2])}>
            {icon}
          </div>
        </div>
        <div className="mt-3 text-3xl font-bold text-white tracking-tight">{value}</div>
        {delta && <div className="mt-1 text-xs text-slate-500">{delta}</div>}
      </div>
    </div>
  );
}
