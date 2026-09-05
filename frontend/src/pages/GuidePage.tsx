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
import { useState } from "react";
import {
  BookOpen, Shield, Globe, Zap, Database, RefreshCw,
  FileText, Briefcase, Newspaper, Building2, Cpu,
  HelpCircle, ExternalLink, Github, Heart, Lock,
  GitMerge, Download,
} from "lucide-react";
import Panel from "../components/Panel";

const sections = [
  {
    id: "overview",
    title: "What is AtlasForge?",
    icon: BookOpen,
    color: "cyan",
    content: (
      <div className="space-y-4 text-sm text-slate-400 leading-relaxed">
        <p>
          <strong className="text-white">AtlasForge</strong> is a real-time intelligence dashboard that aggregates research papers, news articles, job postings, and startup data from multiple public APIs into a single, searchable interface.
        </p>
        <p>
          It was built as an internship assignment with a focus on <strong className="text-white">zero fabrication, zero cost, and full transparency</strong>. Every record displayed comes from a real, publicly accessible API — nothing is hardcoded, demoed, or invented.
        </p>
        <p>
          The system uses a <strong className="text-white">5-layer architecture</strong>: Presentation (React SPA), API (FastAPI), Data (SQLite/Postgres), Services (ingestors + LLM enrichment), and External APIs (arXiv, RSS, RemoteOK, GitHub, etc.).
        </p>
      </div>
    ),
  },
  {
    id: "problem",
    title: "What problem does it solve?",
    icon: HelpCircle,
    color: "violet",
    content: (
      <div className="space-y-4 text-sm text-slate-400 leading-relaxed">
        <p>
          Researchers, founders, and developers currently have to visit <strong className="text-white">10+ different websites</strong> to track AI research (arXiv), industry news (TechCrunch, Verge), job opportunities (RemoteOK, Arbeitnow), and GitHub activity.
        </p>
        <p>
          AtlasForge centralizes all of this into one dashboard with <strong className="text-white">unified search, freshness filtering, and export capabilities</strong>. It also enriches papers with GitHub star counts and uses LLMs to extract organizations and products from news — all automatically.
        </p>
      </div>
    ),
  },
  {
    id: "features",
    title: "Features",
    icon: Zap,
    color: "emerald",
    content: (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { icon: FileText, title: "Research Papers", desc: "Live arXiv feed with title, abstract, authors, categories, PDF links, and GitHub star/fork enrichment." },
          { icon: Newspaper, title: "News Intelligence", desc: "RSS feeds from TechCrunch, The Verge, VentureBeat, MIT News — filtered to 24h freshness." },
          { icon: Briefcase, title: "AI Job Board", desc: "RemoteOK + Arbeitnow APIs filtered for AI/ML roles with salary and remote flags." },
          { icon: Building2, title: "Startup Directory", desc: "Schema ready — ingestor in development. Will track funding, focus areas, and geo data." },
          { icon: Cpu, title: "Product Tracker", desc: "Schema ready — ingestor in development. Will track AI product launches and adoption signals." },
          { icon: GitMerge, title: "Entity Resolution", desc: "Automatically clusters organizations (OpenAI, Google, Meta) using fuzzy matching + LLM extraction." },
          { icon: Database, title: "Pipeline Logs", desc: "Full audit trail of every fetch run — what was fetched, kept, rejected, and why." },
          { icon: Download, title: "Export Center", desc: "Download any module as CSV or TSV for Excel, Google Sheets, or Pandas analysis." },
        ].map((f) => (
          <div key={f.title} className="p-4 rounded-lg bg-white/[0.02] border border-white/5">
            <div className="flex items-center gap-2 mb-2">
              <f.icon size={16} className="text-accent-cyan" />
              <span className="font-medium text-white text-sm">{f.title}</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: "data",
    title: "Data Sources & Legality",
    icon: Globe,
    color: "cyan",
    content: (
      <div className="space-y-4 text-sm text-slate-400 leading-relaxed">
        <div className="p-4 rounded-lg bg-accent-emerald/5 border border-accent-emerald/20">
          <p className="text-accent-emerald font-medium mb-2">All data is 100% free and legal</p>
          <p>Every API used is public, requires no authentication (or uses free-tier keys), and serves data that is already publicly accessible. AtlasForge does not scrape paywalled content, bypass authentication, or violate any Terms of Service.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-slate-500 border-b border-white/5">
                <th className="py-2 font-medium">Module</th>
                <th className="py-2 font-medium">Source</th>
                <th className="py-2 font-medium">Auth Required</th>
                <th className="py-2 font-medium">Cost</th>
              </tr>
            </thead>
            <tbody className="text-slate-400">
              <tr className="border-b border-white/5">
                <td className="py-2">Papers</td>
                <td className="py-2">arXiv Atom API</td>
                <td className="py-2">No</td>
                <td className="py-2 text-accent-emerald">Free</td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-2">News</td>
                <td className="py-2">RSS/Atom feeds (TechCrunch, Verge, VB, MIT)</td>
                <td className="py-2">No</td>
                <td className="py-2 text-accent-emerald">Free</td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-2">Jobs</td>
                <td className="py-2">RemoteOK API + Arbeitnow API</td>
                <td className="py-2">No</td>
                <td className="py-2 text-accent-emerald">Free</td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-2">GitHub Enrichment</td>
                <td className="py-2">GitHub Search API</td>
                <td className="py-2">Optional</td>
                <td className="py-2 text-accent-emerald">Free (60/hr unauthenticated)</td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-2">LLM Extraction</td>
                <td className="py-2">Gemini / Groq / DeepSeek</td>
                <td className="py-2">Optional</td>
                <td className="py-2 text-accent-emerald">Free tier available</td>
              </tr>
              <tr>
                <td className="py-2">Entity Resolution</td>
                <td className="py-2">Local fuzzy matching (RapidFuzz)</td>
                <td className="py-2">No</td>
                <td className="py-2 text-accent-emerald">Free</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    ),
  },
  {
    id: "no-fabrication",
    title: "Real Data, No Fabrication",
    icon: Shield,
    color: "emerald",
    content: (
      <div className="space-y-4 text-sm text-slate-400 leading-relaxed">
        <div className="p-4 rounded-lg bg-accent-amber/5 border border-accent-amber/20">
          <p className="text-accent-amber font-medium mb-2">Our Commitment to Honesty</p>
          <p>AtlasForge will <strong className="text-white">never</strong> fabricate, hallucinate, or invent data. If a data source is unavailable, the UI shows an honest empty state — not fake records.</p>
        </div>
        <ul className="space-y-2 list-disc pl-5">
          <li><strong className="text-white">No seed data:</strong> The database starts empty and populates only via real API calls.</li>
          <li><strong className="text-white">No mock generators:</strong> No code anywhere generates fake papers, news, or jobs.</li>
          <li><strong className="text-white">Deterministic fallback:</strong> If no LLM API keys are configured, the system uses rule-based regex extraction and clearly labels it as <code className="text-accent-violet">method: "deterministic"</code>.</li>
          <li><strong className="text-white">Freshness enforcement:</strong> News older than 24h and jobs older than 72h are rejected at ingest time, not retroactively hidden.</li>
          <li><strong className="text-white">Full audit trail:</strong> Every ingest run logs exactly what was fetched, kept, and rejected.</li>
        </ul>
      </div>
    ),
  },
  {
    id: "auth",
    title: "Authentication & API Keys",
    icon: Lock,
    color: "violet",
    content: (
      <div className="space-y-4 text-sm text-slate-400 leading-relaxed">
        <p>
          <strong className="text-white">No authentication required to use AtlasForge.</strong> The frontend and backend communicate locally with no user login system.
        </p>
        <p>
          <strong className="text-white">Optional API keys</strong> (stored as environment variables, never committed to git) can unlock enhanced features:
        </p>
        <ul className="space-y-2 list-disc pl-5">
          <li><strong className="text-white">GITHUB_TOKEN:</strong> Increases GitHub API rate limit from 60 to 5,000 requests/hour for repo enrichment.</li>
          <li><strong className="text-white">GEMINI_API_KEY / GROQ_API_KEY / DEEPSEEK_API_KEY:</strong> Enables LLM-powered entity extraction from news (free tiers available). Without these, the system uses a deterministic regex fallback.</li>
        </ul>
        <p>All keys are loaded via <code className="text-accent-violet">os.getenv()</code> and have safe defaults. The <code className="text-accent-violet">.env</code> file is gitignored and never shared.</p>
      </div>
    ),
  },
  {
    id: "modules",
    title: "Module Status",
    icon: Database,
    color: "cyan",
    content: (
      <div className="space-y-4 text-sm text-slate-400 leading-relaxed">
        <p>AtlasForge has 5 data modules. Here is their current status:</p>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-slate-500 border-b border-white/5">
                <th className="py-2 font-medium">Module</th>
                <th className="py-2 font-medium">Status</th>
                <th className="py-2 font-medium">Data Source</th>
                <th className="py-2 font-medium">Notes</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-white/5">
                <td className="py-2 text-white">Papers</td>
                <td className="py-2"><span className="text-accent-emerald">Active</span></td>
                <td className="py-2">arXiv API</td>
                <td className="py-2">Fully functional with GitHub enrichment</td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-2 text-white">News</td>
                <td className="py-2"><span className="text-accent-emerald">Active</span></td>
                <td className="py-2">RSS Feeds</td>
                <td className="py-2">24h freshness filter + LLM enrichment</td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-2 text-white">Jobs</td>
                <td className="py-2"><span className="text-accent-emerald">Active</span></td>
                <td className="py-2">RemoteOK + Arbeitnow</td>
                <td className="py-2">72h freshness filter + AI keyword filter</td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-2 text-white">Startups</td>
                <td className="py-2"><span className="text-accent-amber">Schema Ready</span></td>
                <td className="py-2">—</td>
                <td className="py-2">Table exists but no ingestor built yet</td>
              </tr>
              <tr>
                <td className="py-2 text-white">Products</td>
                <td className="py-2"><span className="text-accent-amber">Schema Ready</span></td>
                <td className="py-2">—</td>
                <td className="py-2">Table exists but no ingestor built yet</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    ),
  },
  {
    id: "faq",
    title: "FAQ",
    icon: HelpCircle,
    color: "amber",
    content: (
      <div className="space-y-6">
        {[
          {
            q: "Is AtlasForge free to use?",
            a: "Yes, completely free. All data sources are public APIs with no paid tiers required. The LLM providers (Gemini, Groq, DeepSeek) offer free usage tiers. You will never be charged unless you explicitly sign up for a paid plan on those services.",
          },
          {
            q: "Is the data real or fake?",
            a: "100% real. Every paper, news article, and job posting comes from a live public API. There are no seed files, mock generators, or hardcoded records. If no data is available, the UI shows an honest empty state.",
          },
          {
            q: "Will I get in trouble for using this data?",
            a: "No. All APIs used are public and intended for this kind of access. arXiv, RSS feeds, RemoteOK, and Arbeitnow all allow public access. GitHub's API has generous free limits. We respect rate limits and Terms of Service.",
          },
          {
            q: "Why are Startups and Products empty?",
            a: "The database tables and API endpoints exist, but the data ingestors haven't been built yet. This is intentional — the schema is ready for future expansion. Papers, News, and Jobs are fully functional.",
          },
          {
            q: "Can I deploy this publicly?",
            a: "Yes. The backend (FastAPI) can be deployed on Render, Railway, Fly.io, or any VPS. The frontend (Vite React) can be deployed on Vercel, Netlify, or any static host. For production traffic, swap SQLite for Postgres via one environment variable.",
          },
          {
            q: "Does AtlasForge collect my data?",
            a: "No. There is no user authentication, no tracking, no analytics, and no data collection. The app runs entirely on your machine or your deployed server.",
          },
          {
            q: "What LLM features are optional?",
            a: "LLM enrichment (Gemini, Groq, DeepSeek) is used to extract organizations and products from news text. If no API keys are configured, the system falls back to deterministic regex extraction — it never fabricates.",
          },
          {
            q: "How do I add my own data source?",
            a: "Create a new ingestor in backend/app/services/ingestors/ following the base.py interface, register it in dispatcher.py, and add the API route trigger. The architecture is designed for easy extension.",
          },
        ].map((faq) => (
          <div key={faq.q} className="p-4 rounded-lg bg-white/[0.02] border border-white/5">
            <p className="text-white font-medium text-sm mb-2">{faq.q}</p>
            <p className="text-xs text-slate-500 leading-relaxed">{faq.a}</p>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: "credits",
    title: "Credits & License",
    icon: Heart,
    color: "rose",
    content: (
      <div className="space-y-6">
        <div className="p-6 rounded-lg bg-white/[0.02] border border-white/5">
          <p className="text-white font-medium text-lg mb-4">Developer</p>
          <div className="space-y-3">
            <div>
              <p className="text-white font-medium">Tejas Kamble</p>
              <p className="text-xs text-slate-500">tejaskgm1@gmail.com</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <a href="https://tejas-personal-portfolio-dev.vercel.app/" target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-xs text-accent-cyan hover:underline">
                <Globe size={12} /> Website
              </a>
              <a href="https://www.linkedin.com/in/tejas-kamble-5342443b1" target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-xs text-accent-violet hover:underline">
                <ExternalLink size={12} /> LinkedIn
              </a>
              <a href="https://github.com/tejasworkspacews1-ui" target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-xs text-accent-emerald hover:underline">
                <Github size={12} /> GitHub
              </a>
            </div>
          </div>
        </div>

        <div className="p-6 rounded-lg bg-white/[0.02] border border-white/5">
          <p className="text-white font-medium text-lg mb-2">Open Source License</p>
          <p className="text-xs text-slate-500 leading-relaxed">
            This project is released under the <strong className="text-white">MIT License</strong>. You are free to use, modify, and distribute this code with attribution.
          </p>
        </div>

        <div className="p-6 rounded-lg bg-white/[0.02] border border-white/5">
          <p className="text-white font-medium text-lg mb-2">Attribution</p>
          <p className="text-xs text-slate-500 leading-relaxed">
            When using or referencing AtlasForge, please credit <strong className="text-white">Tejas Kamble</strong> as the original developer.
            Every source file in this repository contains an attribution header with contact details.
          </p>
        </div>

        <div className="p-6 rounded-lg bg-white/[0.02] border border-white/5">
          <p className="text-white font-medium text-lg mb-2">Third-Party Libraries</p>
          <p className="text-xs text-slate-500 leading-relaxed">
            AtlasForge is built with open-source tools including React, TypeScript, FastAPI, SQLAlchemy, Pydantic, Tailwind CSS, Recharts, Lucide icons, and many others.
            We gratefully acknowledge the maintainers of these projects.
          </p>
        </div>
      </div>
    ),
  },
];

export default function GuidePage() {
  const [activeSection, setActiveSection] = useState("overview");

  return (
    <div className="p-8 space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-white tracking-tight">Guide & Documentation</h1>
        <p className="text-sm text-slate-500 mt-1">
          Everything you need to understand AtlasForge — from data sources to legal compliance.
        </p>
      </header>

      <div className="flex gap-2 flex-wrap">
        {sections.map((s) => (
          <button
            key={s.id}
            onClick={() => setActiveSection(s.id)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeSection === s.id
                ? "bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20"
                : "text-slate-400 hover:text-white hover:bg-white/5 border border-transparent"
            }`}
          >
            <s.icon size={12} />
            {s.title}
          </button>
        ))}
      </div>

      <Panel title={sections.find((s) => s.id === activeSection)?.title ?? "Guide"} subtitle="AtlasForge Documentation">
        {sections.find((s) => s.id === activeSection)?.content}
      </Panel>
    </div>
  );
}
