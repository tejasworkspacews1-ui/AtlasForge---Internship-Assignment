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
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import {
  Activity, Database, FileText, Newspaper, Briefcase, Building2,
  GitMerge, Download, BookOpen, Cpu, HelpCircle,
} from "lucide-react";
import CommandCenter from "./pages/CommandCenter";
import PapersPage from "./pages/PapersPage";
import StartupsPage from "./pages/StartupsPage";
import ProductsPage from "./pages/ProductsPage";
import NewsPage from "./pages/NewsPage";
import JobsPage from "./pages/JobsPage";
import EntityResolutionPage from "./pages/EntityResolutionPage";
import ExportPage from "./pages/ExportPage";
import ArchitecturePage from "./pages/ArchitecturePage";
import PipelineLogsPage from "./pages/PipelineLogsPage";
import GuidePage from "./pages/GuidePage";

const nav = [
  { to: "/", label: "Command Center", icon: Activity },
  { to: "/papers", label: "Research Papers", icon: FileText },
  { to: "/startups", label: "Startups", icon: Building2 },
  { to: "/products", label: "Products", icon: Cpu },
  { to: "/news", label: "News", icon: Newspaper },
  { to: "/jobs", label: "Jobs", icon: Briefcase },
  { to: "/entities", label: "Entity Resolution", icon: GitMerge },
  { to: "/pipeline", label: "Pipeline Logs", icon: Database },
  { to: "/export", label: "Export Center", icon: Download },
  { to: "/architecture", label: "Architecture", icon: BookOpen },
  { to: "/guide", label: "Guide", icon: HelpCircle },
];

function Sidebar() {
  return (
    <aside className="w-64 glass border-r border-white/5 flex flex-col">
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-violet flex items-center justify-center shadow-glow">
            <span className="text-obsidian-900 font-black text-lg">A</span>
          </div>
          <div>
            <h1 className="font-bold text-white tracking-tight">AtlasForge</h1>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest">Intelligence Graph</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                isActive
                  ? "bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20"
                  : "text-slate-400 hover:text-white hover:bg-white/5 border border-transparent"
              }`
            }
          >
            <Icon size={16} />
            <span className="font-medium">{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center justify-between text-[10px] text-slate-500 uppercase tracking-wider">
          <span>System</span>
          <span className="flex items-center gap-1.5 text-accent-emerald">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
            Local
          </span>
        </div>
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-obsidian-900 bg-grid-fade">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<CommandCenter />} />
            <Route path="/papers" element={<PapersPage />} />
            <Route path="/startups" element={<StartupsPage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/news" element={<NewsPage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/entities" element={<EntityResolutionPage />} />
            <Route path="/pipeline" element={<PipelineLogsPage />} />
            <Route path="/export" element={<ExportPage />} />
            <Route path="/architecture" element={<ArchitecturePage />} />
            <Route path="/guide" element={<GuidePage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
