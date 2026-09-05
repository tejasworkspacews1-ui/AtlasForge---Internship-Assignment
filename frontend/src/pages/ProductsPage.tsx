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
import Panel from "../components/Panel";
export default function ProductsPage() {
  return (
    <div className="p-8">
      <Panel title="Products" subtitle="Schema ready — no ingestor yet">
        <p className="text-slate-500 text-sm">
          The products table exists in the database schema but no data ingestor has been built yet.
          This module is fully functional once an ingestor is added. Papers, News, and Jobs modules are populated from real public APIs.
        </p>
      </Panel>
    </div>
  );
}
